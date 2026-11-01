import json
from pathlib import Path


def parse_sse(text: str):

    events = []

    for block in text.strip().split("\n\n"):

        name = "message"
        data = None

        for line in block.split("\n"):

            if line.startswith("event:"):

                name = line[len("event:"):].strip()

            elif line.startswith("data:"):

                data = json.loads(
                    line[len("data:"):].strip()
                )

        events.append((name, data))

    return events


def test_chat_streams_and_logs_cost(client):

    body = {
        "messages": [
            {
                "role": "user",
                "content": "What is RAG?"
            }
        ]
    }

    with client.stream(
        "POST",
        "/chat",
        json=body
    ) as r:

        assert r.status_code == 200

        assert r.headers[
            "content-type"
        ].startswith("text/event-stream")

        text = "".join(r.iter_text())

    events = parse_sse(text)

    deltas = [
        d["delta"]
        for name, d in events
        if name == "message"
    ]

    assert "".join(deltas).startswith(
        "You asked: What is RAG?"
    )

    done = [
        d
        for name, d in events
        if name == "done"
    ][0]

    assert done["usage"]["output_tokens"] > 0

    lines = Path(
        client.settings.cost_log_path
    ).read_text().strip().split("\n")

    record = json.loads(lines[-1])

    assert record["provider"] == "fake"
    assert record["ok"] is True
    assert record["cost_usd"] > 0


def test_chat_rejects_bad_input(client):

    r = client.post(
        "/chat",
        json={"messages": []}
    )

    assert r.status_code == 422


def test_chat_rejects_invalid_role(client):

    r = client.post(
        "/chat",
        json={
            "messages": [
                {
                    "role": "hacker",
                    "content": "hi"
                }
            ]
        }
    )

    assert r.status_code == 422