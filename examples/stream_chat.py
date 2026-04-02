#!/usr/bin/env python3
"""Example: Streaming chat with LM Studio.

Usage:
    python examples/stream_chat.py
"""

from src.client import LMStudioClient
from src.health_check import check_server_health


def main() -> None:
    status = check_server_health()
    if not status["healthy"]:
        print(f"Server not reachable: {status['error']}")
        return

    client = LMStudioClient()
    models = client.list_models()
    model_id = models[0]["id"] if models else None

    messages = [{"role": "user", "content": "Tell me a short joke."}]
    print("AI: ", end="", flush=True)
    for chunk in client.chat(messages, model=model_id, stream=True):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
