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
        {"id": "gpt-4.1-mini", "name": "GPT-4.1 Mini", "reasoning": False},
        {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "reasoning": False},
        {"id": "claude-3.5-haiku", "name": "Claude 3.5 Haiku", "reasoning": False},
    ],
    "smart": [
        {"id": "gpt-4.1", "name": "GPT-4.1", "reasoning": False},
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "reasoning": False},
        {"id": "claude-sonnet-4", "name": "Claude Sonnet 4", "reasoning": False},
    ],
    "thinking": [
        {"id": "o3", "name": "GPT o3", "reasoning": True},
        {"id": "o4-mini", "name": "GPT o4-mini", "reasoning": True},
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro Thinking", "reasoning": True},
        {"id": "claude-sonnet-4-thinking", "name": "Claude Sonnet 4 Thinking", "reasoning": True},
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
