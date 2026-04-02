# LM Studio Custom LLM Integration

> Full integration system for communicating with a custom LLM running on
> [LM Studio](https://lmstudio.ai/) via its **OpenAI-compatible API**, designed
> for a dedicated 24 GB RAM remote server and integrated with **TRAE IDE**.

## Architecture

```
+-------------+        OpenAI-compat API        +----------------------+
|  This Repo  |  -----------------------------> |  LM Studio Server    |
|  (client)   |   http://10.0.0.182:1270/v1     |  (remote, 24 GB RAM) |
+-------------+                                 +----------------------+
       |
       +-- src/config.py       - Configuration (env vars / .env)
       +-- src/client.py       - Python client wrapping OpenAI SDK
       +-- src/health_check.py - Server connectivity check
       +-- src/demo.py         - Interactive demo
       +-- .trae/              - TRAE IDE integration settings
```

## Quick Start

### 1. Prerequisites

| Requirement | Details |
|---|---|
| Python | 3.10+ |
| LM Studio | Running on `10.0.0.182:1270` with the local server **started** |
| Network | This machine must be able to reach `10.0.0.182:1270` |

### 2. Install dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure

```bash
# Copy the example env file and edit if needed
cp .env.example .env
```

The defaults point at `http://10.0.0.182:1270/v1`. Edit `.env` if your
server address or model name differs.

### 4. Verify connectivity

```bash
python -m src.health_check
```

Expected output when everything is working:

```
Checking LM Studio server at http://10.0.0.182:1270 ...
Server is healthy!
   Models loaded: ['my-model-name']
```

### 5. Run the demo

```bash
python -m src.demo
```

### 6. Interactive chat example

```bash
python examples/chat.py
```

---

## TRAE IDE Integration

This repository includes pre-built TRAE IDE configuration in the `.trae/` directory.

### Automatic setup (recommended)

1. Open this repository folder in TRAE IDE.
2. TRAE should detect `.trae/settings.json` and configure the AI provider
   automatically.

### Manual setup in TRAE

If TRAE does not pick up the settings automatically, configure the OpenAI-
compatible provider manually:

1. Open **TRAE Settings** (Ctrl/Cmd + ,).
2. Navigate to **AI / Model Provider**.
3. Select **OpenAI Compatible** (or "Custom Provider").
4. Fill in:
   - **API Base URL**: `http://10.0.0.182:1270/v1`
   - **API Key**: `lm-studio` (any non-empty string works)
   - **Model**: the model identifier shown by `python -m src.health_check`
5. Save and restart TRAE.

### Verifying in TRAE

Open TRAE's AI chat panel and send a test message. If you get a response,
the integration is working.

---

## Using the Python Client in Your Own Code

```python
from src.client import LMStudioClient

client = LMStudioClient()

# Chat completion
reply = client.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing in one paragraph."},
])
print(reply)

# Streaming
for chunk in client.chat(
    [{"role": "user", "content": "Tell me a joke."}],
    stream=True,
):
    print(chunk, end="", flush=True)
print()

# List loaded models
print(client.list_models())

# Legacy text completion
text = client.complete("Once upon a time,")
print(text)
```

---

## Configuration Reference

All settings are controlled via environment variables (loaded from `.env`):

| Variable | Default | Description |
|---|---|---|
| `LM_STUDIO_BASE_URL` | `http://10.0.0.182:1270/v1` | OpenAI-compat API base URL |
| `LM_STUDIO_API_KEY` | `lm-studio` | API key (LM Studio accepts any non-empty string) |
| `LM_STUDIO_MODEL` | `default` | Model identifier |
| `LM_STUDIO_MAX_TOKENS` | `2048` | Max tokens per response |
| `LM_STUDIO_TEMPERATURE` | `0.7` | Sampling temperature |
| `LM_STUDIO_REQUEST_TIMEOUT` | `120` | Request timeout in seconds |

---

## Troubleshooting

### "Cannot connect to http://10.0.0.182:1270"

1. Confirm LM Studio is **running** on the remote server.
2. In LM Studio, go to the **Local Server** tab and click **Start Server**.
3. Make sure the server is bound to `0.0.0.0` (not `127.0.0.1`) so it
   accepts remote connections.
4. Check firewall rules — port `1270` must be open on the remote machine.
5. Test from this machine: `curl http://10.0.0.182:1270/v1/models`

### "Model not found" or empty model list

- Load a model in LM Studio's UI before starting the server.
- Run `python -m src.health_check` to see which models are loaded.

### TRAE IDE does not use the custom model

- Double-check the API Base URL ends with `/v1`.
- Make sure the API key field is not empty (use `lm-studio`).
- Restart TRAE after changing settings.

### Timeout errors

- Large models on 24 GB RAM may need more time to generate.
- Increase `LM_STUDIO_REQUEST_TIMEOUT` in `.env` (e.g., `300`).
- In TRAE, increase the timeout in `.trae/settings.json`.

---

## Project Structure

```
.
+-- .env.example            # Environment variable template
+-- .trae/
|   +-- settings.json       # TRAE IDE AI provider config
|   +-- openai_override.json# OpenAI-compat override for TRAE
+-- requirements.txt        # Python dependencies
+-- src/
|   +-- __init__.py
|   +-- config.py           # Configuration loader
|   +-- client.py           # LM Studio client (OpenAI SDK wrapper)
|   +-- health_check.py     # Server health check utility
|   +-- demo.py             # Quick demo script
+-- examples/
|   +-- chat.py             # Interactive chat example
|   +-- stream_chat.py      # Streaming example
+-- tests/
    +-- __init__.py
    +-- test_lm_studio.py   # Unit tests
```

## License

MIT
