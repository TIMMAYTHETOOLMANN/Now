"""Tests for the LM Studio configuration and client modules."""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.config import LMStudioConfig


class TestLMStudioConfig(unittest.TestCase):
    """Unit tests for LMStudioConfig."""

    def test_defaults(self):
        """Config should fall back to sensible defaults."""
        config = LMStudioConfig()
        self.assertIn("10.0.0.182", config.base_url)
        self.assertEqual(config.api_key, "lm-studio")
        self.assertEqual(config.max_tokens, 2048)
        self.assertAlmostEqual(config.temperature, 0.7)
        self.assertEqual(config.request_timeout, 120)

    @patch.dict(os.environ, {"LM_STUDIO_BASE_URL": "http://localhost:9999/v1"})
    def test_env_override(self):
        """Config should respect environment variable overrides."""
        config = LMStudioConfig()
        self.assertEqual(config.base_url, "http://localhost:9999/v1")

    def test_server_origin(self):
        """server_origin should strip the /v1 path."""
        config = LMStudioConfig(base_url="http://10.0.0.182:1270/v1")
        self.assertEqual(config.server_origin, "http://10.0.0.182:1270")


class TestLMStudioClient(unittest.TestCase):
    """Unit tests for LMStudioClient (mocked network)."""

    def test_list_models(self):
        """list_models should return parsed model dicts."""
        from src.client import LMStudioClient

        client = LMStudioClient(
            config=LMStudioConfig(base_url="http://10.0.0.182:1270/v1")
        )

        mock_model = MagicMock()
        mock_model.id = "test-model"
        mock_model.object = "model"
        mock_response = MagicMock()
        mock_response.data = [mock_model]

        with patch.object(client._client.models, "list", return_value=mock_response):
            models = client.list_models()
            self.assertEqual(len(models), 1)
            self.assertEqual(models[0]["id"], "test-model")

    def test_chat(self):
        """chat should return the assistant content."""
        from src.client import LMStudioClient

        client = LMStudioClient(
            config=LMStudioConfig(base_url="http://10.0.0.182:1270/v1")
        )

        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from LM Studio!"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(
            client._client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            result = client.chat([{"role": "user", "content": "Hi"}])
            self.assertEqual(result, "Hello from LM Studio!")

    def test_complete(self):
        """complete should return generated text."""
        from src.client import LMStudioClient

        client = LMStudioClient(
            config=LMStudioConfig(base_url="http://10.0.0.182:1270/v1")
        )

        mock_choice = MagicMock()
        mock_choice.text = "Generated text"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(
            client._client.completions,
            "create",
            return_value=mock_response,
        ):
            result = client.complete("Once upon a time")
            self.assertEqual(result, "Generated text")


class TestHealthCheck(unittest.TestCase):
    """Unit tests for the health check utility."""

    @patch("src.health_check.requests.get")
    def test_healthy_server(self, mock_get):
        """Should report healthy when server returns model list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [{"id": "my-model", "object": "model"}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        from src.health_check import check_server_health

        status = check_server_health()
        self.assertTrue(status["healthy"])
        self.assertIn("my-model", status["models"])

    @patch("src.health_check.requests.get")
    def test_unreachable_server(self, mock_get):
        """Should report unhealthy when server is unreachable."""
        import requests as req

        mock_get.side_effect = req.ConnectionError("refused")

        from src.health_check import check_server_health

        status = check_server_health()
        self.assertFalse(status["healthy"])
        self.assertIn("Cannot connect", status["error"])


if __name__ == "__main__":
    unittest.main()
