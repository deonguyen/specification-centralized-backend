import os
from google.cloud import secretmanager
import google.auth
from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from google.oauth2 import service_account


def get_gcp_credential():
    try:
        credentials = None
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        google_creds_path = os.path.realpath(os.environ.get("GOOGLE_CREDENTIALS_FILE"))
        if google_creds_path and os.path.exists(google_creds_path):
            credentials = service_account.Credentials.from_service_account_file(
                google_creds_path,
                scopes=scopes,
            )
        else:
            # Use Application Default Credentials. This works for local dev (gcloud auth),
            # GKE (Workload Identity), and Cloud Run (attached service account).
            credentials, project = google.auth.default(scopes=scopes)
        return credentials
    except Exception as e:
        print(f"Failed to retrieve service account credentials: {e}")
        return None


def get_gcp_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieve a secret payload from Google Cloud Secret Manager using Application Default Credentials.

    Args:
        secret_id (str): The ID/name of the secret in Secret Manager.
        version_id (str): The version of the secret to fetch. Defaults to "latest".

    Returns:
        str: The decoded string value of the secret, or None if retrieval fails.
    """
    try:
        project_id = SpecificationCentralizedSpecConfig.GOOGLE_PROJECT_ID or os.environ.get(
            "GOOGLE_PROJECT_ID"
        )

        credentials = None
        google_creds_path = os.path.realpath(os.environ.get("GOOGLE_CREDENTIALS_FILE"))
        if google_creds_path and os.path.exists(google_creds_path):
            credentials = service_account.Credentials.from_service_account_file(
                google_creds_path
            )
        else:
            # Use Application Default Credentials. This works for local dev (gcloud auth),
            # GKE (Workload Identity), and Cloud Run (attached service account).
            credentials, project = google.auth.default()

        client = secretmanager.SecretManagerServiceClient(credentials=credentials)

        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(
            f"Failed to retrieve secret '{secret_id}' from project '{project_id}': {e}"
        )
        return None
