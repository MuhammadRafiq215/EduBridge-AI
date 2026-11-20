"""Provider-agnostic AI teacher backend for EduBridge AI."""
from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from urllib.parse import urlparse
from typing import Any, Protocol

MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


class ChatProvider(Protocol):
    """Minimal interface required by the EduBridge AI Teacher UI."""
    def answer(
        self,
        messages: list[dict[str, Any]],
        profile_context: dict[str, Any] | None = None,
        image: tuple[bytes, str] | None = None,
        knowledge_context: str | None = None,
    ) -> str: ...


def build_profile_context(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a small allow-listed education context; omit unrelated fields."""
    if not isinstance(profile, dict):
        return None
    keys = ("country", "level", "qualification", "custom_qualification", "board", "pathway", "programme",
            "current_year", "subjects", "confidence", "latest_results")
    context = {key: profile[key] for key in keys if key in profile and profile[key] not in (None, "", [], {})}
    return context or None


def validate_image(image_bytes: bytes, mime_type: str) -> None:
    """Reject unsupported, empty or oversized image uploads before transmission."""
    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Please upload a PNG, JPEG or WebP image.")
    if not image_bytes:
        raise ValueError("The selected image is empty.")
    signatures = {
        "image/png": image_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": image_bytes.startswith(b"\xff\xd8\xff"),
        "image/webp": len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP",
    }
    if not signatures[mime_type]:
        raise ValueError("The file content does not match its image type.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("Please choose an image smaller than 5 MB.")


def build_system_prompt(
    profile_context: dict[str, Any] | None,
    knowledge_context: str | None = None,
) -> str:
    profile_text = json.dumps(profile_context, ensure_ascii=False) if profile_context else "No learner profile was supplied."
    prompt = (
        "You are EduBridge AI, a patient educational tutor. Explain concepts clearly, step by step, "
        "at the learner's level. Ask a brief clarifying question when the question or image is unclear. "
        "For academic problems, explain the reasoning, not just the final answer. Never invent exam-board "
        "rules, grade statistics, citations, or sources. Distinguish verified facts from general guidance "
        "and say when you are uncertain. Do not claim to have checked live syllabuses or global grade "
        "distributions. Encourage independent learning. Do not request passwords, identity numbers, or "
        "other sensitive personal information. When official evidence is supplied, cite only exact "
        "[SPEC:source_id] labels present in that evidence. Distinguish verified snippets, subject "
        "specifications, catalogues and historical references; never present one as another. "
        "If a year, session, subject or version is not supported by the evidence, say so.\n"
        f"Learner education context (user-provided profile fields): {profile_text}"
    )
    if knowledge_context:
        prompt += "\n\nCURATED KNOWLEDGE BASE CONTEXT:\n" + knowledge_context
    return prompt


def build_request_messages(
    messages: list[dict[str, Any]],
    profile_context: dict[str, Any] | None = None,
    image: tuple[bytes, str] | None = None,
    knowledge_context: str | None = None,
) -> list[dict[str, Any]]:
    """Build a conversation with optional image and verified knowledge context."""
    result: list[dict[str, Any]] = [{
        "role": "system",
        "content": build_system_prompt(profile_context, knowledge_context),
    }]
    for item in messages[-12:]:
        role, content = item.get("role"), item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            result.append({"role": role, "content": content})
    if image:
        image_bytes, mime_type = image
        validate_image(image_bytes, mime_type)
        data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
        result.append({"role": "user", "content": [
            {"type": "text", "text": "Interpret this educational image or screenshot and explain it. If text or diagrams are unclear, say so."},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]})
    return result


def extract_response_text(payload: dict[str, Any]) -> str:
    """Extract text from a standard OpenAI-compatible chat completion response."""
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("The AI provider returned an unexpected response format.") from exc
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        combined = "\n".join(part for part in parts if isinstance(part, str) and part.strip())
        if combined:
            return combined.strip()
    raise ValueError("The AI provider returned an empty response.")


def validate_hosted_base_url(base_url: str) -> str:
    """Accept only well-formed HTTPS endpoints for hosted model providers."""
    value = str(base_url or "").strip()
    if not value or any(character.isspace() for character in value):
        raise ValueError("Hosted AI endpoints must be valid HTTPS URLs.")
    parsed = urlparse(value)
    try:
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Hosted AI endpoint has an invalid port.") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Hosted AI endpoints must use HTTPS and cannot contain credentials, query strings or fragments.")
    return value.rstrip("/")


class OpenAICompatibleProvider:
    """Adapter for providers exposing the OpenAI-compatible Chat Completions API."""
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", timeout: int = 45):
        if not api_key.strip() or not model.strip():
            raise ValueError("An API key and model name are required.")
        self.api_key, self.model = api_key.strip(), model.strip()
        self.base_url = validate_hosted_base_url(base_url)
        self.timeout = max(15, min(int(timeout), 120))
        self.supports_vision = False
        self.provider_name = "Hosted AI provider"

    def answer(
        self,
        messages: list[dict[str, Any]],
        profile_context: dict[str, Any] | None = None,
        image: tuple[bytes, str] | None = None,
        knowledge_context: str | None = None,
    ) -> str:
        request_messages = build_request_messages(messages, profile_context, image, knowledge_context)
        body = json.dumps({"model": self.model, "messages": request_messages, "temperature": 0.3}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise RuntimeError("The AI provider rejected the configured credentials. Check the AI settings.") from exc
            if exc.code == 429:
                raise RuntimeError("The AI provider rate limit was reached. Please wait and try again.") from exc
            raise RuntimeError(f"The AI provider returned HTTP {exc.code}. Please try again later.") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError("EduBridge could not reach the AI provider. Check the provider settings or try again later.") from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeError("The AI provider returned an unreadable response.") from exc
        return extract_response_text(payload)


class LocalModelProvider:
    """Connect to a local Ollama-compatible server without an API account or key.

    The server must run on the same machine as Streamlit. Loopback-only URLs
    prevent this setting from becoming a general server-side request proxy.
    """
    def __init__(self, model: str, base_url: str = "http://127.0.0.1:11434", timeout: int = 120):
        parsed = urlparse(base_url.strip())
        if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("Local AI must use an http://localhost, 127.0.0.1 or ::1 address.")
        if not model.strip():
            raise ValueError("Enter the name of a model already installed in your local model server.")
        self.model = model.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = max(15, min(int(timeout), 240))
        self.supports_vision = False
        self.provider_name = "Local AI model"

    def answer(
        self,
        messages: list[dict[str, Any]],
        profile_context: dict[str, Any] | None = None,
        image: tuple[bytes, str] | None = None,
        knowledge_context: str | None = None,
    ) -> str:
        request_messages = build_request_messages(messages, profile_context, image, knowledge_context)
        local_messages = []
        for item in request_messages:
            content = item.get("content", "")
            row = {"role": item["role"], "content": content if isinstance(content, str) else ""}
            if isinstance(content, list):
                texts, images = [], []
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") == "text":
                        texts.append(str(part.get("text", "")))
                    elif part.get("type") == "image_url":
                        url = part.get("image_url", {}).get("url", "")
                        if isinstance(url, str) and url.startswith("data:") and "," in url:
                            images.append(url.split(",", 1)[1])
                row["content"] = "\\n".join(texts)
                if images:
                    row["images"] = images
            local_messages.append(row)

        body = json.dumps({
            "model": self.model,
            "messages": local_messages,
            "stream": False,
            "options": {"temperature": 0.3},
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Local AI server returned HTTP {exc.code}. Check that the model server is running.") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            raise RuntimeError(
                "EduBridge cannot reach the local AI server. Start the local model service and run Streamlit on the same computer."
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeError("The local AI server returned an unreadable response.") from exc
        answer = payload.get("message", {}).get("content") if isinstance(payload, dict) else None
        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("The local AI model returned an empty response.")
        return answer.strip()


def build_provider_from_settings(settings: dict[str, Any] | None):
    """Build an explicitly configured local or OpenAI-compatible provider."""
    if not isinstance(settings, dict):
        return None
    provider_type = str(settings.get("provider", "openai_compatible")).strip().lower()
    model = str(settings.get("model", "")).strip()
    if not model:
        return None
    try:
        timeout = int(settings.get("timeout", 60))
    except (TypeError, ValueError):
        timeout = 60

    if provider_type == "local":
        base_url = str(settings.get("base_url", "http://127.0.0.1:11434")).strip()
        provider = LocalModelProvider(model=model, base_url=base_url, timeout=timeout)
        provider.supports_vision = bool(settings.get("supports_vision", False))
        return provider
    if provider_type == "openai_compatible":
        api_key = str(settings.get("api_key", "")).strip()
        if not api_key:
            return None
        base_url = str(settings.get("base_url", "https://api.openai.com/v1")).strip()
        provider = OpenAICompatibleProvider(api_key=api_key, model=model, base_url=base_url, timeout=timeout)
        provider.supports_vision = bool(settings.get("supports_vision", False))
        provider.provider_name = "Configured AI provider"
        return provider
    raise ValueError("AI provider must be 'local' or 'openai_compatible'.")
