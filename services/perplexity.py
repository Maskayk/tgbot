import base64
import logging
from typing import Optional

import aiohttp

from config import PERPLEXITY_API_KEY, PERPLEXITY_BASE_URL

logger = logging.getLogger(__name__)

SONAR_MODELS = {"sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro"}


async def chat_completion(
    messages: list[dict],
    model: str = "sonar",
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 4096,
    reasoning: bool = False,
    reasoning_effort: str = "medium",
    web_search: bool = True,
) -> dict:
    """Send a request to Perplexity API and return the response."""

    is_sonar = model in SONAR_MODELS

    if is_sonar:
        return await _sonar_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            web_search=web_search,
        )
    else:
        return await _agent_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            reasoning=reasoning,
            reasoning_effort=reasoning_effort,
        )


async def _sonar_completion(
    messages: list[dict],
    model: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    web_search: bool,
) -> dict:
    """Chat Completions API for Sonar models."""
    url = f"{PERPLEXITY_BASE_URL}/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    if not web_search:
        payload["search_recency_filter"] = "none"

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("Perplexity Sonar API error %d: %s", resp.status, error_text)
                    return {"error": True, "message": f"Ошибка API ({resp.status}). Попробуйте позже."}
                data = await resp.json()
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                return {"error": False, "content": content, "citations": citations}
    except aiohttp.ClientError as e:
        logger.error("Perplexity Sonar request failed: %s", e)
        return {"error": True, "message": "Не удалось связаться с Perplexity. Попробуйте позже."}
    except Exception as e:
        logger.error("Unexpected error in Sonar completion: %s", e)
        return {"error": True, "message": "Произошла непредвиденная ошибка."}


async def _agent_completion(
    messages: list[dict],
    model: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    reasoning: bool,
    reasoning_effort: str,
) -> dict:
    """Agent API for third-party models (OpenAI, Anthropic, Google, xAI)."""
    url = f"{PERPLEXITY_BASE_URL}/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }

    if reasoning:
        payload["reasoning_effort"] = reasoning_effort

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=180)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error("Perplexity Agent API error %d: %s", resp.status, error_text)
                    return {"error": True, "message": f"Ошибка API ({resp.status}). Попробуйте позже."}
                data = await resp.json()
                content = data["choices"][0]["message"]["content"]
                citations = data.get("citations", [])
                return {"error": False, "content": content, "citations": citations}
    except aiohttp.ClientError as e:
        logger.error("Perplexity Agent request failed: %s", e)
        return {"error": True, "message": "Не удалось связаться с Perplexity. Попробуйте позже."}
    except Exception as e:
        logger.error("Unexpected error in Agent completion: %s", e)
        return {"error": True, "message": "Произошла непредвиденная ошибка."}


def build_messages_with_image(
    text: str,
    image_data: bytes,
    history: list[dict],
) -> list[dict]:
    """Build messages list with an image encoded as base64 data URI."""
    b64 = base64.b64encode(image_data).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{b64}"

    user_content = [
        {"type": "image_url", "image_url": {"url": data_uri}},
        {"type": "text", "text": text},
    ]

    messages = list(history)
    messages.append({"role": "user", "content": user_content})
    return messages


def build_messages_text(text: str, history: list[dict]) -> list[dict]:
    """Build messages list for a text-only request."""
    messages = list(history)
    messages.append({"role": "user", "content": text})
    return messages
