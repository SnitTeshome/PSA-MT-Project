"""Pluggable LLM backends for the dict-prompted Ekegusii mechanism.

Every backend here is bring-your-own-credential -- nothing in this repo can
authenticate to any of these on its own, and no credential is ever written to
disk by this module (the app keeps them in `st.session_state` for the browser
session only). Pick one in the app's setup screen.

Deliberately not included: any backend tied to this project's own private cloud
compute (used during development, not something a teammate can authenticate to
without being handed personal/paid access).
"""

import time

import requests

NO_ECHO_INSTRUCTION = (
    "Respond with ONLY the Ekegusii translation as a single line of natural Ekegusii "
    "text. Do not repeat this system message, the glossary, the examples, or the "
    "English source sentence. Do not explain your answer."
)


class BackendError(RuntimeError):
    pass


BACKENDS = {
    "cohere": {
        "label": "Cohere (command-a-03-2025)",
        "fields": [("api_key", "API key", True)],
        "help": (
            "Free trial key, no cost for light interactive use: "
            "dashboard.cohere.com -> API Keys."
        ),
    },
    "bedrock": {
        "label": "AWS Bedrock (Llama 3 70B Instruct)",
        "fields": [
            ("access_key_id", "AWS Access Key ID", True),
            ("secret_access_key", "AWS Secret Access Key", True),
            ("region", "AWS Region (default us-east-1)", False),
        ],
        "help": (
            "AWS Console -> IAM -> Users -> Security credentials -> Create access "
            "key. Then Bedrock Console -> Model access -> request Llama 3 70B "
            "Instruct (approval is usually instant, no cost until you call it)."
        ),
    },
    "azure_openai": {
        "label": "Azure OpenAI",
        "fields": [
            ("endpoint", "Resource endpoint (https://<resource>.openai.azure.com)", True),
            ("api_key", "API key", True),
            ("deployment", "Deployment name", True),
        ],
        "help": (
            "Azure Portal -> create an Azure OpenAI resource -> Keys and Endpoint. "
            "Then Azure AI Studio -> Deployments -> deploy a chat model and note "
            "the deployment name you gave it."
        ),
    },
    "custom": {
        "label": "Custom OpenAI-compatible endpoint",
        "fields": [
            ("base_url", "Base URL (no trailing /chat/completions)", True),
            ("api_key", "API key (leave blank if none required)", False),
            ("model", "Model name", True),
        ],
        "help": (
            "For any self-hosted or third-party OpenAI-compatible chat-completions "
            "endpoint you already have access to (e.g. your own hosted vLLM "
            "deployment)."
        ),
    },
    "local": {
        "label": "Local model on your own machine (Ollama or similar)",
        "fields": [
            ("base_url", "Base URL", True),
            ("model", "Model name (e.g. llama3.1:8b)", True),
            ("api_key", "API key (usually not needed)", False),
        ],
        "defaults": {"base_url": "http://localhost:11434/v1"},
        "warning": (
            "This project's validated numbers (chrF 54.8 agriculture, 38.6 "
            "cross-domain) were measured against much larger hosted models "
            "(Llama 3 70B, Qwen2.5 72B). A small local model (7B-8B class, what "
            "most laptops can realistically run) will very likely produce "
            "noticeably worse output for this mechanism -- expect more "
            "degenerate/repetitive translations and more retries. CPU-only "
            "inference can also take a long time per sentence, and a large "
            "enough model to compete with the hosted backends generally needs "
            "far more RAM/VRAM than a typical laptop has. Reasonable for "
            "offline experimentation; not a like-for-like substitute for the "
            "other backends above."
        ),
        "help": (
            "Point this at a local OpenAI-compatible server already running on "
            "your own machine -- Ollama's default is http://localhost:11434/v1 "
            "with no API key needed; llama.cpp's server and LM Studio work the "
            "same way. Start the server and pull a model first (e.g. "
            "`ollama pull llama3.1:8b`)."
        ),
    },
}


def call_llm(backend_name, credentials, messages, temperature=0, max_tokens=300, retries=4):
    if backend_name == "cohere":
        return _call_cohere(credentials, messages, temperature, max_tokens, retries)
    if backend_name == "bedrock":
        return _call_bedrock(credentials, messages, temperature, max_tokens, retries)
    if backend_name == "azure_openai":
        return _call_azure_openai(credentials, messages, temperature, max_tokens, retries)
    if backend_name in ("custom", "local"):
        return _call_custom(credentials, messages, temperature, max_tokens, retries)
    raise BackendError(f"Unknown backend: {backend_name!r}")


def _call_cohere(creds, messages, temperature, max_tokens, retries):
    headers = {"Authorization": f"Bearer {creds['api_key']}", "Content-Type": "application/json"}
    last_error = None
    for attempt in range(retries):
        body = {
            "model": "command-a-03-2025",
            "max_tokens": max_tokens,
            "temperature": temperature if attempt == 0 else min(temperature + 0.3, 1.0),
            "messages": messages,
        }
        try:
            resp = requests.post("https://api.cohere.com/v2/chat", headers=headers, json=body, timeout=90)
        except requests.exceptions.RequestException as e:
            last_error = f"network error: {e}"
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code == 200:
            data = resp.json()
            return data["message"]["content"][0]["text"].strip().strip('"')
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code == 422 and "NO_VALID_RESPONSE_GENERATED" in resp.text:
            last_error = resp.text[:300]
            time.sleep(2)
            continue
        raise BackendError(f"Cohere API error {resp.status_code}: {resp.text[:500]}")
    raise BackendError(f"Cohere: giving up after {retries} attempts, last error: {last_error}")


def _call_bedrock(creds, messages, temperature, max_tokens, retries):
    import boto3

    client = boto3.client(
        "bedrock-runtime",
        region_name=creds.get("region") or "us-east-1",
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
    )
    system_text = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_text = next((m["content"] for m in messages if m["role"] == "user"), "")
    for attempt in range(retries):
        try:
            resp = client.converse(
                modelId="meta.llama3-70b-instruct-v1:0",
                system=[{"text": system_text}],
                messages=[{"role": "user", "content": [{"text": user_text}]}],
                inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
            )
            return resp["output"]["message"]["content"][0]["text"].strip().strip('"')
        except Exception as e:
            msg = str(e)
            if "ThrottlingException" in msg or "TooManyRequestsException" in msg:
                time.sleep(3 * (attempt + 1))
                continue
            raise BackendError(f"Bedrock error: {msg[:300]}")
    raise BackendError("Bedrock: giving up after retries (throttled)")


def _call_azure_openai(creds, messages, temperature, max_tokens, retries):
    endpoint = creds["endpoint"].rstrip("/")
    deployment = creds["deployment"]
    api_version = creds.get("api_version") or "2024-10-21"
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"api-key": creds["api_key"], "Content-Type": "application/json"}
    last_error = None
    for attempt in range(retries):
        body = {"messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=90)
        except requests.exceptions.RequestException as e:
            last_error = f"network error: {e}"
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        raise BackendError(f"Azure OpenAI error {resp.status_code}: {resp.text[:500]}")
    raise BackendError(f"Azure OpenAI: giving up after {retries} attempts, last error: {last_error}")


def _call_custom(creds, messages, temperature, max_tokens, retries):
    base_url = creds["base_url"].rstrip("/")
    headers = {"Content-Type": "application/json"}
    if creds.get("api_key"):
        headers["Authorization"] = f"Bearer {creds['api_key']}"
    last_error = None
    for attempt in range(retries):
        body = {"model": creds["model"], "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        try:
            resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=body, timeout=90)
        except requests.exceptions.RequestException as e:
            last_error = f"network error: {e}"
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip().strip('"')
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        raise BackendError(f"Custom endpoint error {resp.status_code}: {resp.text[:500]}")
    raise BackendError(f"Custom endpoint: giving up after {retries} attempts, last error: {last_error}")
