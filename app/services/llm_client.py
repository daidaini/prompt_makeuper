from openai import AsyncOpenAI
from app.config import settings
from app.services.llm_logger import log_llm_interaction


class LLMClient:
    """OpenAI-compatible LLM client for async completions."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.flash_client = None

    def _get_flash_client(self) -> AsyncOpenAI:
        if self.flash_client is None:
            self.flash_client = AsyncOpenAI(
                api_key=settings.FLASH_API_KEY or settings.OPENAI_API_KEY,
                base_url=settings.FLASH_BASE_URL or settings.OPENAI_BASE_URL,
            )
        return self.flash_client

    @log_llm_interaction
    async def chat(self, messages: list, stage: str = None, skill_name: str = None, iteration: int = None, **kwargs) -> str:
        """
        Simple chat completion with optional logging context.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stage: Pipeline stage for logging (skill_selection, skill_application, quality_check)
            skill_name: Name of skill being applied
            iteration: Iteration number for refinement loops
            **kwargs: Additional arguments for the completion

        Returns:
            The assistant's response content
        """
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            **kwargs
        )
        return response.choices[0].message.content

    @log_llm_interaction
    async def chat_flash(self, messages: list, stage: str = None, skill_name: str = None, iteration: int = None, **kwargs) -> str:
        """
        Chat completion using the flash model configuration.

        Args:
            messages: List of message dicts with 'role' and 'content'
            stage: Pipeline stage for logging
            skill_name: Name of skill being applied
            iteration: Iteration number for refinement loops
            **kwargs: Additional arguments for the completion

        Returns:
            The assistant's response content
        """
        response = await self._get_flash_client().chat.completions.create(
            model=settings.FLASH_MODEL or settings.OPENAI_MODEL,
            messages=messages,
            temperature=settings.TEMPERATURE,
            **kwargs
        )
        return response.choices[0].message.content
