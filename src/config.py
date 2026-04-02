"""Configuration module for LM Studio server connection.

Loads settings from environment variables (via .env file) and exposes them
as a typed configuration object used by the rest of the application.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_PATH)


@dataclass(frozen=True)
class LMStudioConfig:
    """Immutable configuration for the LM Studio server."""

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "LM_STUDIO_BASE_URL", "http://10.0.0.182:1270/v1"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("LM_STUDIO_API_KEY", "lm-studio")
    )
    model: str = field(
        default_factory=lambda: os.getenv("LM_STUDIO_MODEL", "default")
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LM_STUDIO_MAX_TOKENS", "2048"))
    )
    temperature: float = field(
        default_factory=lambda: float(
            os.getenv("LM_STUDIO_TEMPERATURE", "0.7")
        )
    )
    request_timeout: int = field(
        default_factory=lambda: int(
            os.getenv("LM_STUDIO_REQUEST_TIMEOUT", "120")
        )
    )

    @property
    def server_origin(self) -> str:
        """Return the scheme + host + port without the /v1 path."""
        return self.base_url.replace("/v1", "").rstrip("/")
