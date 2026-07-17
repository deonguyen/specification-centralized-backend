from django.db.models import Q
from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from specification_centralized_core.models.component_model import ComponentModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.services import specification_service
from specification_centralized_spec.services.specification_service import parse_specification_content
from specification_centralized_spec.views.vertex_ai_view import VertexAIView
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import base64
import markdown
from bs4 import BeautifulSoup
import re
from rest_framework import permissions, viewsets, status


def initialize_google_drive_service():
    """
    Authenticate and build the Google Drive service using existing service account credentials.
    """
    credentials = service_account.Credentials.from_service_account_file(
        SpecificationCentralizedSpecConfig.GOOGLE_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=credentials)


def list_google_drive_files(service, folder_id, path=""):
    """
    Recursively fetch files and folders from a specific Google Drive folder ID.
    """
    tree_data = []
    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None

    try:
        while True:
            try:
                response = (
                    service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                        pageToken=page_token,
                    )
                    .execute()
                )
            except HttpError as error:
                if error.resp.status in [401, 403]:
                    print("Token expired or unauthorized, refreshing token to keep long running list file...")
                    service = initialize_google_drive_service()
                    response = (
                        service.files()
                        .list(
                            q=query,
                            spaces="drive",
                            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                            pageToken=page_token,
                        )
                        .execute()
                    )
                else:
                    raise error

            for file in response.get("files", []):
                file_path = f"{path}/{file['name']}".strip("/")

                if file["mimeType"] == "application/vnd.google-apps.folder":
                    # Recurse into subdirectories
                    tree_data.extend(
                        list_google_drive_files(service, file["id"], file_path)
                    )
                else:
                    # Add files filtered by .md extension and inside 'SWRD' folder
                    if "swrd" in file_path.lower() and file["name"].lower().endswith(
                        ".md"
                    ):
                        raw_content = get_google_drive_file_content(
                            service, file["id"], file["mimeType"]
                        )
                        (
                            req_id,
                            interface_content,
                            parsed_spec_content,
                            sub_spec_content,
                        ) = specification_service.parse_specification_content(
                            raw_content
                        )
                        if req_id:
                            tree_data.append(
                                {
                                    "path": file_path,
                                    "type": "blob",
                                    "id": file["id"],
                                    "name": file["name"],
                                    "mimeType": file["mimeType"],
                                    "modifiedTime": file["modifiedTime"],
                                    "raw_content": raw_content,
                                    "req_id": req_id,
                                    "interface_content": interface_content,
                                    "parsed_spec_content": parsed_spec_content,
                                    "sub_spec_content": sub_spec_content,
                                }
                            )
                            print(f"Added file: {file_path} (ID: {file['id']})")
                        else:
                            print(f"Skipped file (no req_id found): {file_path} (ID: {file['id']})")
                            
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break
    except Exception as e:
        print(f"Error fetching files from Google Drive: {e}")

    return tree_data


def get_google_drive_file_content(service, file_id, mime_type):
    """
    Download file content. Exports Google Docs to plain text.
    """
    try:
        if mime_type == "application/vnd.google-apps.document":
            # Google Docs cannot be downloaded directly; they must be exported
            request = service.files().export_media(
                fileId=file_id, mimeType="text/plain"
            )
        else:
            # For regular files uploaded to drive (like .md, .txt)
            request = service.files().get_media(fileId=file_id)

        return request.execute().decode("utf-8")
    except HttpError as error:
        if error.resp.status in [401, 403]:
            print("Token expired during file download, refreshing token...")
            service = initialize_google_drive_service()
            if mime_type == "application/vnd.google-apps.document":
                request = service.files().export_media(
                    fileId=file_id, mimeType="text/plain"
                )
            else:
                request = service.files().get_media(fileId=file_id)
            return request.execute().decode("utf-8")
        print(f"Failed to fetch content for file {file_id}: {error}")
        return None
    except Exception as e:
        print(f"Failed to fetch content for file {file_id}: {e}")
        return None
