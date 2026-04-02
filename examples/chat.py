#!/usr/bin/env python3
"""Example: Quick interactive chat with LM Studio.

Usage:
    python examples/chat.py
"""

from src.client import LMStudioClient
from src.health_check import check_server_health


def main() -> None:
    # 1. Verify connectivity
    status = check_server_health()
    if not status["healthy"]:
        print(f"Server not reachable: {status['error']}")
        return

    print(f"Connected! Models available: {status['models']}")
    client = LMStudioClient()

    # 2. Optionally pick a model
    models = client.list_models()
    if models:
        model_id = models[0]["id"]
        print(f"Using model: {model_id}")
    else:
        model_id = None

    # 3. Simple conversation loop
    print("\nType 'quit' to exit.\n")
    history: list[dict] = []
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        try:
            reply = client.chat(history, model=model_id)
            print(f"AI:  {reply}\n")
            history.append({"role": "assistant", "content": reply})
        except Exception as exc:
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    main()
