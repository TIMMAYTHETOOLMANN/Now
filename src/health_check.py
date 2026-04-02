"""Health-check utility for the LM Studio server.

Run directly to verify connectivity:

    python -m src.health_check

Or import and call ``check_server_health()`` programmatically.
"""

from __future__ import annotations

import sys

import requests

from .config import LMStudioConfig


def check_server_health(config: LMStudioConfig | None = None) -> dict:
    """Ping the LM Studio server and return a status dict.

    Returns
    -------
    dict
        ``{"healthy": True/False, "models": [...], "error": "..."}``
    """
    config = config or LMStudioConfig()
    result: dict = {"healthy": False, "models": [], "error": None}

    # 1. Basic connectivity – hit the /v1/models endpoint
    models_url = f"{config.base_url}/models"
    try:
        resp = requests.get(models_url, timeout=config.request_timeout)
        resp.raise_for_status()
    except requests.ConnectionError:
        result["error"] = (
            f"Cannot connect to {config.server_origin}. "
            "Ensure LM Studio is running and the server is started."
        )
        return result
    except requests.Timeout:
        result["error"] = (
            f"Request to {models_url} timed out after "
            f"{config.request_timeout}s."
        )
        return result
    except requests.HTTPError as exc:
        result["error"] = f"HTTP error from server: {exc}"
        return result

    # 2. Parse model list
    try:
        data = resp.json()
        models = [m.get("id", "unknown") for m in data.get("data", [])]
        result["models"] = models
    except (ValueError, KeyError) as exc:
        result["error"] = f"Unexpected response format: {exc}"
        return result

    result["healthy"] = True
    return result


def main() -> None:
    """CLI entry-point for a quick health check."""
    config = LMStudioConfig()
    print(f"Checking LM Studio server at {config.server_origin} …")
    status = check_server_health(config)

    if status["healthy"]:
        print("✅  Server is healthy!")
        print(f"   Models loaded: {status['models']}")
    else:
        print(f"❌  Server is NOT healthy: {status['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
