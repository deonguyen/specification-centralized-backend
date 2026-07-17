import os
import time
import jwt
import requests
from django.core.cache import cache
from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from specification_centralized_spec.services.encryption_service import get_decrypted_env_value
from specification_centralized_spec.services.google_cloud_service import get_gcp_secret
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None


def get_github_app_installation_token():
    """
    Generates a GitHub App installation token.
    It caches the token to avoid regenerating it on every request.
    """
    cached_token = cache.get("github_installation_token")
    if cached_token:
        return cached_token

    encryption_key = None
    if get_gcp_secret:
        gcp_secret_key = os.environ.get("GOOGLE_SECRET_KEY_ENCRYPTION_KEY")
        encryption_key = get_gcp_secret(gcp_secret_key)

    github_app_id = getattr(SpecificationCentralizedSpecConfig, "GITHUB_APP_ID", None)    
    github_app_installation_id = getattr(
        SpecificationCentralizedSpecConfig, "GITHUB_APP_INSTALLATION_ID", None
    )

    github_app_private_key = None
    encrypted_key_path = getattr(
        SpecificationCentralizedSpecConfig, "GITHUB_APP_ENCRYPTED_PRIVATE_KEY_PATH", None
    )

    if encrypted_key_path and encryption_key and Fernet and os.path.exists(encrypted_key_path):
        try:
            with open(encrypted_key_path, "rb") as key_file:
                encrypted_key = key_file.read()
            cipher_suite = Fernet(encryption_key.encode("utf-8"))
            github_app_private_key = cipher_suite.decrypt(encrypted_key)
        except Exception as e:
            print(f"Warning: Failed to load or decrypt GitHub App private key from {encrypted_key_path} - {e}")
    else:
        github_app_private_key = getattr(SpecificationCentralizedSpecConfig, "GITHUB_APP_PRIVATE_KEY", None)
    
    # 1. Generate JWT
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),  # 10 minutes expiration
        "iss": github_app_id,
    }

    try:
        github_jwt = jwt.encode(payload, github_app_private_key, algorithm="RS256")
    except Exception:
        return None # Could not encode JWT

    # 2. Get Installation Access Token
    headers = {
        "Authorization": f"Bearer {github_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{github_app_installation_id}/access_tokens"

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("token")
        cache.set("github_installation_token", token, timeout=3500)  # Cache for just under an hour
        return token
    except requests.RequestException:
        return None