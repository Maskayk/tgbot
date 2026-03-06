import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1061467560"))

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"

# Model definitions grouped by category
MODELS = {
    "fast": [
        {"id": "openai/gpt-5-mini", "name": "GPT-5 Mini", "reasoning": False},
        {"id": "google/gemini-2.5-flash", "name": "Gemini 2.5 Flash", "reasoning": False},
        {"id": "xai/grok-4-1-fast-non-reasoning", "name": "Grok 4.1 Fast", "reasoning": False},
    ],
    "smart": [
        {"id": "openai/gpt-5.2", "name": "GPT-5.2", "reasoning": False},
        {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "reasoning": False},
        {"id": "anthropic/claude-sonnet-4-5", "name": "Claude Sonnet 4.5", "reasoning": False},
    ],
    "thinking": [
        {"id": "openai/gpt-5.2", "name": "GPT-5.2 Thinking", "reasoning": True},
        {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro Thinking", "reasoning": True},
        {"id": "xai/grok-4-1", "name": "Grok 4.1 Thinking", "reasoning": True},
    ],
    "search": [
        {"id": "sonar", "name": "Sonar", "reasoning": False},
        {"id": "sonar-pro", "name": "Sonar Pro", "reasoning": False},
        {"id": "sonar-reasoning", "name": "Sonar Reasoning", "reasoning": True},
        {"id": "sonar-reasoning-pro", "name": "Sonar Reasoning Pro", "reasoning": True},
    ],
}

CATEGORY_NAMES = {
    "fast": "⚡ Быстрые",
    "smart": "🧠 Умные",
    "thinking": "💭 Думающие",
    "search": "🔍 Поисковые",
}

# Default user settings
DEFAULT_SETTINGS = {
    "model_id": "sonar",
    "model_name": "Sonar",
    "reasoning": False,
    "model_supports_reasoning": False,
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 4096,
    "reasoning_effort": "medium",
    "web_search": True,
}

MAX_HISTORY_MESSAGES = 20
DB_PATH = "storage/database.json"
