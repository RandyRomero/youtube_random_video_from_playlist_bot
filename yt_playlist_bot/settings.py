import os

# logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
JSON_LOGS = os.getenv("ENV_VAR", "False").lower() in ("true", "1", "t")

BOT_TOKEN = os.environ["BOT_TOKEN"]
