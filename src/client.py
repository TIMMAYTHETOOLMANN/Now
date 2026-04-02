"""Client module for communicating with LM Studio via the OpenAI-compatible API.

This module provides a high-level ``LMStudioClient`` class that wraps the
official ``openai`` Python SDK, pointing it at the local/remote LM Studio
server instead of the OpenAI cloud.
"""

from __future__ import annotations

from typing import Generator, Optional

from openai import OpenAI

from .config import LMStudioConfig


class LMStudioClient:
    """Thin wrapper around the OpenAI SDK configured for LM Studio."""

    def __init__(self, config: Optional[LMStudioConfig] = None) -> None:
        self.config = config or LMStudioConfig()
        self._client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.request_timeout,
        )

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def list_models(self) -> list[dict]:
        """Return a list of models currently loaded in LM Studio."""
        response = self._client.models.list()
        return [{"id": m.id, "object": m.object} for m in response.data]

    def chat(
        self,
        messages: list[dict],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Send a chat-completion request.

        Parameters
        ----------
        messages:
            List of message dicts, e.g.
            ``[{"role": "user", "content": "Hello!"}]``
        model:
            Override the default model identifier.
        max_tokens:
            Override the default max tokens.
        temperature:
            Override the default temperature.
        stream:
            If ``True``, return a generator that yields content chunks.

        Returns
        -------
        str or Generator[str, None, None]
            The assistant's reply (or a streaming generator).
        """
        params = {
            "model": model or self.config.model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": (
                temperature if temperature is not None else self.config.temperature
            ),
            "stream": stream,
        }

        if stream:
            return self._stream_chat(params)

        response = self._client.chat.completions.create(**params)
        return response.choices[0].message.content

    def complete(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send a legacy text-completion request.

        Parameters
        ----------
        prompt:
            The prompt string.

        Returns
        -------
        str
            The generated text.
        """
        response = self._client.completions.create(
            model=model or self.config.model,
            prompt=prompt,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=(
                temperature if temperature is not None else self.config.temperature
            ),
        )
        return response.choices[0].text

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _stream_chat(self, params: dict) -> Generator[str, None, None]:
        """Yield content chunks from a streaming chat completion."""
        stream = self._client.chat.completions.create(**params)
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
