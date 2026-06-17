"""Shared Podio OAuth credential access from environment variables."""

from .env_config import require_env


def get_podio_oauth_credentials():
    """Return Podio password-grant credentials (raises if any are missing)."""
    return {
        'client_id': require_env('PODIO_CLIENT_ID'),
        'client_secret': require_env('PODIO_CLIENT_SECRET'),
        'username': require_env('PODIO_USERNAME'),
        'password': require_env('PODIO_PASSWORD'),
    }
