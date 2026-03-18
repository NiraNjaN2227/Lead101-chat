import logging
import time
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any


from app.services.llm_service import LLMService
from app.services.student_service import StudentService
from app.services.cache_service import get_cache_service
from app.intelligence.intent_detector import IntentDetector
from app.intelligence.context_builder import ContextBuilder
from app.agents.response_templates import generate_template_response
from app.agents.knowledge_base import search_knowledge
from app.core.config import settings

# Re-using existing session memory if compatible, or simple dict for now
# The original code imported from app.memory.session_memory import SessionMemory
from app.memory.session_memory import SessionMemory

logger = logging.getLogger(__name__)


def _trim_history_by_tokens(history: list, max_tokens: int = 1500) -> list:
    """
    Keep the most recent messages that fit within an estimated token budget.
    Approximation: 1 token ≈ 4 characters.
    """
    budget = max_tokens
    trimmed = []
    for msg in reversed(history):
        est_tokens = len(msg["content"]) // 4
        if budget - est_tokens < 0:
            break
        trimmed.insert(0, msg)
        budget -= est_tokens
    return trimmed

class Orchestrator:
    """
    Async Orchestrator — 3-Tier Response Architecture
    """

    def __init__(self):
        self.llm_service = LLMService()
        self.student_service = StudentService()
        self.cache_service = get_cache_service()
        self.intent_detector = IntentDetector()
        self.session_memory = SessionMemory()
        self.context_builder = ContextBuilder()

        # Simple Metrics Tracking
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "tier1_hits": 0,
            "tier2_hits": 0,
            "tier3_hits": 0,
            "total_latency_seconds": 0.0,
        }

        # Load system prompt from external file (app/prompts/system_prompt.txt)
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
        try:
            self._system_prompt = prompt_path.read_text(encoding="utf-8")
            logger.info(f"System prompt loaded from {prompt_path}")
        except FileNotFoundError:
            logger.warning(f"system_prompt.txt not found at {prompt_path}. Using inline fallback.")
            self._system_prompt = (
                "You are an AI-powered Student Assistant for a university. "
                "Help students with their academic and personal information in a polite, professional, and concise manner. "
                "Never invent student data. Only use verified information provided by the system."
            )

    async def _get_student_context(self, session_id: str, user_message: str, phone: str = "") -> Optional[Dict[str, Any]]:
        """
        Resolves student identity from session, phone, or message content.
        """
        # 1. Check Session
        student_id = self.session_memory.get_student_id(session_id)
        
        # 2. Check Phone (WhatsApp)
        if not student_id and phone:
            student = await self.student_service.search_student_by_phone(phone)
            if student:
                student_id = student["student_id"]
                self.session_memory.set_student_id(session_id, student_id)
                return student

        # 3. Check Message for ID pattern
        if not student_id:
            match = re.search(settings.STUDENT_ID_PATTERN, user_message.upper())
            if match:
                student_id = match.group(0)
                # Verify existence
                student = await self.student_service.get_student(student_id)
                if student:
                    self.session_memory.set_student_id(session_id, student_id)
                    return student

        if student_id:
             return await self.student_service.get_student(student_id)
             
        return None

    async def process_message(
        self,
        user_message: str,
        student_id: str = "",
        session_id: str = "default_session",
        phone: str = "",
    ) -> str:
        self.metrics["total_requests"] += 1
        start_time = time.time()
        
        # 0. Normalise message for consistent cache keying
        import hashlib
        _normalised = user_message.lower().strip()
        msg_hash = hashlib.md5(_normalised.encode()).hexdigest()
        cache_key = f"{student_id}:{session_id}:{msg_hash}"
        cached_response = await self.cache_service.get(cache_key)
        if cached_response:
            self.metrics["cache_hits"] += 1
            latency = time.time() - start_time
            self.metrics["total_latency_seconds"] += latency
            logger.info(f"Cache Hit. Latency: {latency:.4f}s")
            return cached_response

        # 1. Resolve Student
        student = await self._get_student_context(session_id, user_message, phone)
        # If student_id was passed explicitly in args, override/set
        if student_id and not student:
             student = await self.student_service.get_student(student_id)
             if student:
                 self.session_memory.set_student_id(session_id, student_id)

        # 2. Detect Language & Intent
        # Simplified language detection for now (assuming English or handing it to LLM)
        intent, confidence = self.intent_detector.detect(user_message)
        logger.info(f"Intent: {intent} (Conf: {confidence})")
        
        response = ""
        
        # 3. Tier 1: Structured / Template
        # Only if we have student data and high confidence intent
        if student and confidence > 0.8:
            relevant_data = ContextBuilder.build_context(intent, student)
            # generate_template_response is sync, but fast
            template_reply = generate_template_response(intent, relevant_data)
            if template_reply:
                response = template_reply
                self.metrics["tier1_hits"] += 1
                logger.info("Tier 1 Response")
            else:
                logger.warning(
                    f"Tier 1 template returned None for intent='{intent}'. "
                    "Falling through to Tier 2/3."
                )

        # 4. Tier 2: Knowledge Base
        if not response:
            kb_answer = search_knowledge(user_message)
            if kb_answer:
                response = kb_answer
                self.metrics["tier2_hits"] += 1
                logger.info("Tier 2 Response")

        # 5. Tier 3: LLM Fallback
        if not response:
            logger.info("Tier 3 Response (LLM)")
            
            # Build Context
            # If student found, minimize context. If not, minimal context.
            context_data = ContextBuilder.build_context(intent, student) if student else {}
            
            history = _trim_history_by_tokens(
                self.session_memory.get_history(session_id),
                max_tokens=settings.MAX_HISTORY_TOKENS
            )
            
            messages = [{"role": "system", "content": self._system_prompt}]
            
            # Add history
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add generic context if student not identified
            if not student:
                messages.append({
                    "role": "system", 
                    "content": "No student identified yet. Capture student ID (format STU2026XXXX) if possible. Greet: 'Hello! I'm your AI Student Assistant. Please provide your Student ID to continue.' or 'It seems the Student ID format is incorrect. Please provide it in this format: STU2026XXXX.'"
                })
            
            # Add Data Context
            if context_data:
                messages.append({
                    "role": "system",
                    "content": f"Student Data Context (Use ONLY this): {json.dumps(context_data)}"
                })
                
            messages.append({"role": "user", "content": user_message})

            try:
                response = await self.llm_service.generate_response(messages)
            except Exception as e:
                logger.error(f"LLM Failed: {e}")
                response = "I'm experiencing some technical difficulties. Please try again later."
                
            self.metrics["tier3_hits"] += 1

        # 6. Save interactions & Cache
        self.session_memory.add_message(session_id, "user", user_message, intent)
        self.session_memory.add_message(session_id, "assistant", response)
        
        await self.cache_service.set(cache_key, response, ttl=600)
        
        latency = time.time() - start_time
        self.metrics["total_latency_seconds"] += latency
        logger.info(f"Total Latency: {latency:.4f}s")
        
        return response
