import json
import time
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import Settings, get_settings
from app.cost import log_call
from app.llm.base import LLMError, StreamResult
from app.llm.factory import build_provider
from app.schemas import ChatRequest

app = FastAPI(
    title="MetricMint",
    description="Trustworthy answers on new-age tech companies' unit economics.",
    version="0.1.0"
)


SettingsDep = Annotated[
    Settings,
    Depends(get_settings)
]


def get_provider(settings: SettingsDep):
    return build_provider(settings)


ProviderDep = Annotated[
    object,
    Depends(get_provider)
]


@app.get("/health")
def health(settings: SettingsDep) -> dict:

    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment
    }


@app.get("/ready")
def ready(settings: SettingsDep):

    if not settings.database_url:

        return {
            "status": "ready",
            "database": "not configured"
        }

    try:

        with psycopg.connect(
            settings.database_url,
            connect_timeout=3
        ) as conn:

            conn.execute("SELECT 1")

        return {
            "status": "ready",
            "database": "ok"
        }

    except Exception as exc:

        return JSONResponse(
            status_code=503,
            content={
                "status": "not ready",
                "database": str(exc)[:200]
            }
        )


def sse(
    data: dict,
    event: str | None = None
) -> str:

    prefix = f"event: {event}\n" if event else ""

    return (
        f"{prefix}data: {json.dumps(data)}\n\n"
    )


@app.post("/chat")
async def chat(
    req: ChatRequest,
    settings: SettingsDep,
    provider: ProviderDep
):

    async def event_stream():

        result = StreamResult()

        start = time.perf_counter()

        ok = True

        try:

            async for piece in provider.stream_chat(
                req.messages,
                req.temperature,
                result
            ):

                yield sse({
                    "delta": piece
                })

        except LLMError as exc:

            ok = False

            yield sse(
                {"error": str(exc)},
                event="error"
            )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        record = log_call(
            settings.cost_log_path,
            provider=provider.name,
            model=provider.model,
            usage=result.usage,
            latency_ms=latency_ms,
            price_in_per_m=settings.price_input_per_million,
            price_out_per_m=settings.price_output_per_million,
            ok=ok
        )

        yield sse(
            {
                "usage": result.usage.model_dump(),
                "cost_usd": record["cost_usd"]
            },
            event="done"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )