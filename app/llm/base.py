from collections.abc import AsyncIterator
from typing import Protocol

from app.schemas import Message, Usage


class StreamResult:

    def __init__(self) -> None:
        self.usage = Usage()


class LLMProvider(Protocol):

    name: str
    model: str

    def stream_chat(
        self,
        messages: list[Message],
        temperature: float,
        result: StreamResult
    ) -> AsyncIterator[str]:

        ...


class LLMError(Exception):
    """Raised when the provider fails after retries."""