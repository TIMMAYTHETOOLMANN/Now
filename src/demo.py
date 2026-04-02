"""Interactive demo – quick way to verify your LM Studio connection.

Usage:
    python -m src.demo
"""

from __future__ import annotations

from .client import LMStudioClient
from .health_check import check_server_health


def main() -> None:
    print("=" * 60)
    print("  LM Studio – Connection Demo")
    print("=" * 60)

    # Step 1 – health check
    status = check_server_health()
    if not status["healthy"]:
        print(f"\n❌ Server unreachable: {status['error']}")
        print("Please make sure LM Studio is running and the server is started.")
        return

    print(f"\n✅ Server is healthy.  Models: {status['models']}")

    # Step 2 – send a test chat message
    client = LMStudioClient()
    print("\nSending test prompt: 'Say hello in one sentence.'")
    reply = client.chat([{"role": "user", "content": "Say hello in one sentence."}])
    print(f"\n🤖 Model response:\n{reply}\n")


if __name__ == "__main__":
    main()
