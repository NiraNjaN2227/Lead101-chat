import logging
from typing import Dict, List
from openai import AsyncOpenAI, OpenAIError, APIError, AuthenticationError
from app.core.config import settings
from app.core.exceptions import LLMServiceException

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.max_retries = settings.LLM_MAX_RETRIES

        if not self.api_key or self.api_key == "":
            logger.error("OPENAI_API_KEY is missing or empty. LLM calls will fail.")
            raise LLMServiceException("OPENAI_API_KEY not configured.")

        # Initialize Async Client using official SDK format
        try:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            # Validation log to ensure key is loaded (only log prefix for security)
            key_prefix = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "INVALID"
            logger.info(f"LLM Service initialized. Model: {self.model} | Key loaded: {key_prefix}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise LLMServiceException(f"LLM Client Init Error: {e}")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generates a response using the OpenAI SDK (Async).
        """
        try:
            logger.debug("Sending request to LLM...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # OpenAI SDK returns an object, not dict
            content = response.choices[0].message.content
            
            # Log usage if available
            if response.usage:
                logger.info(f"LLM Success. Tokens: {response.usage.total_tokens} (Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens})")
            
            return content

        except AuthenticationError:
            logger.error("LLM Authentication Failed: Invalid API Key.")
            raise LLMServiceException("Invalid API Key.")
        except APIError as e:
            logger.error(f"LLM API Error: {e}")
            raise LLMServiceException(f"LLM API Error: {e}")
        except OpenAIError as e:
            logger.error(f"LLM Gen Error: {e}")
            raise LLMServiceException(f"LLM Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected LLM Error: {e}")
            raise LLMServiceException(f"Unexpected Error: {e}")
