from app.config import Settings
from app.llm.fake import FakeProvider
from app.llm.openai_compat import OpenAICompatProvider


def build_provider(settings: Settings):

    if settings.llm_provider == "fake":
        return FakeProvider()

    if settings.llm_provider == "openai_compat":

        return OpenAICompatProvider(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            backoff_base_seconds=(
                settings.llm_backoff_base_seconds
            )
        )

    raise ValueError(
        f"unknown LLM_PROVIDER: {settings.llm_provider}"
    )