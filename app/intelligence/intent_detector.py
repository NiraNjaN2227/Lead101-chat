import re
import logging
from typing import Tuple
from difflib import get_close_matches

logger = logging.getLogger(__name__)


class IntentDetector:
    """
    Hybrid Intent Detection — 3 tiers:
    1. Exact Regex/Keyword Match (confidence 1.0) — fastest
    2. Fuzzy Match for typos (confidence 0.8) — robust
    3. Sentence-Embedding Similarity (confidence 0.6–0.9) — smartest, lazy-loaded
    """

    # ── Tier 1: Keyword maps ──────────────────────────────────────────────────
    INTENTS = {
        "greeting":         ["hi", "hello", "hey", "good morning", "greetings"],
        "fees":             ["fee", "fees", "payment", "cost", "price", "charge", "amount", "due", "paid"],
        "admission_status": ["admission", "status", "application", "enrolled", "seat"],
        "course":           ["course", "subject", "branch", "stream", "syllabus", "courses"],
        "documents":        ["document", "documents", "certificate", "mark sheet", "upload", "verify"],
        "contact":          ["contact", "phone", "email", "support", "help", "address"],
        "profile":          ["profile", "my data", "my details", "name", "address"],
    }

    # ── Tier 3: Natural-language examples per intent (for embedding matching) ──
    INTENT_EXAMPLES = {
        "fees": [
            "what are my fees",
            "how much do I owe",
            "pending payment amount",
            "what is the fee amount",
            "how much money do I need to pay",
            "show me my fee details",
            "what is my remaining balance",
        ],
        "admission_status": [
            "what is my admission status",
            "am I admitted",
            "was my application accepted",
            "did I get a seat",
            "is my enrollment confirmed",
        ],
        "course": [
            "what course am I enrolled in",
            "what is my branch",
            "which stream did I get",
            "tell me about my course",
            "what subjects do I have",
        ],
        "documents": [
            "document status",
            "have my documents been verified",
            "which certificates do I need to upload",
            "is my marksheet submitted",
        ],
        "contact": [
            "how to contact support",
            "who is my counselor",
            "what is the helpline number",
            "give me the support email",
        ],
        "profile": [
            "show me my profile",
            "what are my personal details",
            "tell me my name and address",
            "view my information",
        ],
        "greeting": [
            "hi there",
            "hello how are you",
            "good morning",
            "hey",
        ],
    }

    def __init__(self):
        # Lazy-loaded — model is only loaded the first time embedding fallback is needed
        self._model = None
        self._intent_embeddings: dict = {}

    # ── Lazy model loader ─────────────────────────────────────────────────────
    def _load_embedding_model(self) -> None:
        """Load sentence-transformer model on first use."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._intent_embeddings = {
                intent: self._model.encode(examples, convert_to_tensor=True)
                for intent, examples in self.INTENT_EXAMPLES.items()
            }
            logger.info("Sentence-transformers model loaded successfully.")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Embedding intent fallback is disabled. "
                "Run: pip install sentence-transformers"
            )
            self._model = "unavailable"

    # ── Public API ────────────────────────────────────────────────────────────
    def detect(self, text: str) -> Tuple[str, float]:
        """
        Detects intent and returns (intent_name, confidence_score).

        Confidence levels:
            1.0  — Exact keyword match
            0.8  — Fuzzy keyword match
            0.6+ — Embedding cosine similarity
            0.0  — No match (unknown)
        """
        text_clean = text.lower().strip()

        # ── Tier 1: Exact keyword match ───────────────────────────────────────
        for intent, keywords in self.INTENTS.items():
            for word in keywords:
                if re.search(r'\b' + re.escape(word) + r'\b', text_clean):
                    logger.debug(f"Intent (Exact): {intent}")
                    return intent, 1.0

        # ── Tier 2: Fuzzy keyword match ───────────────────────────────────────
        all_keywords = [kw for kws in self.INTENTS.values() for kw in kws]
        for word in text_clean.split():
            matches = get_close_matches(word, all_keywords, n=1, cutoff=0.8)
            if matches:
                matched_kw = matches[0]
                for intent, keywords in self.INTENTS.items():
                    if matched_kw in keywords:
                        logger.debug(f"Intent (Fuzzy): {intent} (matched '{matched_kw}')")
                        return intent, 0.8

        # ── Tier 3: Embedding similarity fallback ─────────────────────────────
        self._load_embedding_model()
        if self._model and self._model != "unavailable":
            try:
                from sentence_transformers import util as st_util
                query_embedding = self._model.encode(text_clean, convert_to_tensor=True)

                best_intent = "unknown"
                best_score = 0.0

                for intent, intent_embeddings in self._intent_embeddings.items():
                    # Cosine similarity between query and all examples for this intent
                    scores = st_util.cos_sim(query_embedding, intent_embeddings)
                    max_score = float(scores.max())
                    if max_score > best_score:
                        best_score = max_score
                        best_intent = intent

                # Only accept if similarity is high enough
                EMBEDDING_THRESHOLD = 0.45
                if best_score >= EMBEDDING_THRESHOLD:
                    confidence = round(min(best_score, 0.95), 2)
                    logger.debug(
                        f"Intent (Embedding): {best_intent} "
                        f"(score={best_score:.3f}, conf={confidence})"
                    )
                    return best_intent, confidence
            except Exception as e:
                logger.error(f"Embedding intent detection failed: {e}")

        return "unknown", 0.0
