"""Tests for fallback model and GET /usage."""
import asyncio

import httpx
import pytest

from app.llm.base import LLMError, StreamResult
from app.llm.fake import FakeProvider
from app.llm.fallback import FallbackProvider
from app.llm.openai_compat import OpenAICompatProvider
from app.schemas import Message

MSGS = [
    Message(role="user", content="hello")
]


def slow_main(handler):
    return OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="k",
        model="main-model",
        max_retries=1,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(handler),
    )


def collect(provider):
    result = StreamResult()

    async def run():
        return "".join([
            piece
            async for piece in provider.stream_chat(
                MSGS,
                0.2,
                result,
            )
        ])

    return asyncio.run(run()), result


def test_fallback_activated_on_main_failure():
    def handler(request):
        return httpx.Response(503)

    backup = FakeProvider(model="backup-model")
    fb = FallbackProvider(slow_main(handler), backup)

    text, result = collect(fb)

    assert "fake answer" in text
    assert result.fallback_used is True
    assert result.model == "backup-model"


def test_fallback_not_activated_on_success():
    def handler(request):
        return httpx.Response(
            200,
            content=b'data: {"choices":[{"delta":{"content":"ok"}}]}\n\ndata: [DONE]\n\n',
        )

    backup = FakeProvider(model="backup-model")
    fb = FallbackProvider(slow_main(handler), backup)

    text, result = collect(fb)

    assert text == "ok"
    assert result.fallback_used is False


def test_fallback_does_not_mask_mid_stream_failure():
    class BrokenStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'data: {"choices":[{"delta":{"content":"start"}}]}\n\n'
            raise httpx.ReadTimeout("broken connection")

    def handler(request):
        return httpx.Response(200, stream=BrokenStream())

    backup = FakeProvider(model="backup-model")
    fb = FallbackProvider(slow_main(handler), backup)

    with pytest.raises(LLMError):
        collect(fb)


def test_usage_endpoint(client):
    r_empty = client.get("/usage")
    assert r_empty.status_code == 200
    assert r_empty.json() == {}

    with client.stream(
        "POST",
        "/chat",
        json={"messages": [{"role": "user", "content": "What is unit economics?"}]},
    ) as r:
        assert r.status_code == 200
        _ = "".join(r.iter_text())

    r_usage = client.get("/usage")
    assert r_usage.status_code == 200
    data = r_usage.json()
    assert len(data) == 1
    day = list(data.keys())[0]
    assert data[day]["calls"] == 1
    assert data[day]["input_tokens"] > 0
    assert data[day]["output_tokens"] > 0
    assert data[day]["cost_usd"] > 0
