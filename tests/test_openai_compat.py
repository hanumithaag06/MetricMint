import asyncio
import json

import httpx
import pytest

from app.llm.base import LLMError, StreamResult
from app.llm.openai_compat import OpenAICompatProvider, backoff_delay
from app.schemas import Message

MSGS = [
    Message(role="user", content="hello")
]


def sse_body(pieces, usage=None):

    lines = []

    for p in pieces:

        lines.append(
            "data: " + json.dumps({
                "choices": [
                    {
                        "delta": {
                            "content": p
                        }
                    }
                ]
            })
        )

    if usage:

        lines.append(
            "data: " + json.dumps({
                "choices": [],
                "usage": usage
            })
        )

    lines.append("data: [DONE]")

    return (
        "\n\n".join(lines) + "\n\n"
    ).encode()


def provider(handler, retries=3):

    return OpenAICompatProvider(
        base_url="http://test/v1",
        api_key="k",
        model="m",
        max_retries=retries,
        backoff_base_seconds=0.0,
        transport=httpx.MockTransport(handler)
    )


def collect(p):

    result = StreamResult()

    async def run():

        return "".join([
            piece
            async for piece in p.stream_chat(
                MSGS,
                0.2,
                result
            )
        ])

    return asyncio.run(run()), result


def test_streams_text_and_reads_usage():

    def handler(request):

        assert request.headers[
            "Authorization"
        ] == "Bearer k"

        return httpx.Response(
            200,
            content=sse_body(
                ["Hel", "lo"],
                {
                    "prompt_tokens": 7,
                    "completion_tokens": 2
                }
            )
        )

    text, result = collect(provider(handler))

    assert text == "Hello"

    assert result.usage.input_tokens == 7
    assert result.usage.output_tokens == 2
    assert result.usage.estimated is False


def test_retries_on_503_then_succeeds():

    calls = {"n": 0}

    def handler(request):

        calls["n"] += 1

        if calls["n"] < 3:
            return httpx.Response(503)

        return httpx.Response(
            200,
            content=sse_body(["ok"])
        )

    text, result = collect(provider(handler))

    assert text == "ok"
    assert calls["n"] == 3
    assert result.usage.estimated is True


def test_does_not_retry_on_401():

    calls = {"n": 0}

    def handler(request):

        calls["n"] += 1

        return httpx.Response(
            401,
            json={"error": "bad key"}
        )

    with pytest.raises(LLMError):
        collect(provider(handler))

    assert calls["n"] == 1


def test_gives_up_after_max_retries_on_timeout():

    calls = {"n": 0}

    def handler(request):

        calls["n"] += 1

        raise httpx.ReadTimeout(
            "slow",
            request=request
        )

    with pytest.raises(LLMError):
        collect(provider(handler, retries=2))

    assert calls["n"] == 3


def test_backoff_is_bounded():

    for attempt in range(10):

        assert (
            0 <= backoff_delay(
                attempt,
                base=0.5,
                cap=8.0
            ) <= 8.0
        )