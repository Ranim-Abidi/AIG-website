"""
Environment variable loading and helpers.
Loads variables from a .env file at the project root (never commit .env).
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_LOADED = False


def load_dotenv():
    """Load KEY=VALUE pairs from project-root .env into os.environ."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    env_path = PROJECT_ROOT / '.env'
    if env_path.is_file():
        for raw_line in env_path.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

    _ENV_LOADED = True


def env(key, default=None):
    load_dotenv()
    return os.environ.get(key, default)


def env_bool(key, default=False):
    value = env(key)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(key, default=''):
    value = env(key, default)
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def require_env(key):
    value = env(key)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{key}'. "
            f"Copy .env.example to .env and set your credentials."
        )
    return value
