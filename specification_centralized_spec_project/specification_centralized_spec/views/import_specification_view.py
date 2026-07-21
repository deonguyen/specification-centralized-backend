from specification_centralized_core.models.notification_model import NotificationModel
from specification_centralized_core.models.project_model import ProjectModel
from django.contrib.auth.models import User
from specification_centralized_spec.services.github_app_service import get_github_app_installation_token
from specification_centralized_spec.services.import_specification_service import (
    process_import_specification_from_github,
    process_import_specification_from_jama,
    process_import_specification_from_local,
    process_import_specification_from_google_drive,
)
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import os
import tempfile
import re
import threading
from django.db import close_old_connections
import zipfile
import tarfile
import shutil
from django.conf import settings

class ImportSpecificationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def import_specification_from_local_file(self, request):
        """
        Uploads a zip file, extracts it, and syncs the .md files to project specifications.
        Expects 'file', 'project_id', and 'version' in the request data.
        """
        uploaded_file = request.FILES.get("file")
        current_version = request.data.get("version")
        project_id = request.data.get("project_id")

        if not all([uploaded_file, project_id, current_version]):
            return Response(
                {"error": "Parameters 'file', 'project_id', and 'version' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = ProjectModel.objects.get(id=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        base_dir = os.environ.get("LOCAL_TEMP_UPLOAD_FILE_BASE_DIR")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)

        temp_dir = tempfile.mkdtemp(dir=base_dir)
        file_path = os.path.join(temp_dir, uploaded_file.name)

        # Save the uploaded file to the temporary path before starting the thread
        with open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        def run_local_import(project, file_path, temp_dir, current_version, user):
            try:
                # Check for archive formats and extract if found
                if zipfile.is_zipfile(file_path):
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                    # The base for relative paths is the directory where files were extracted
                    base_dir = temp_dir
                elif tarfile.is_tarfile(file_path):
                    with tarfile.open(file_path, "r:*") as tar_ref:
                        tar_ref.extractall(path=temp_dir)
                    base_dir = temp_dir
                else:
                    # If not a zip or tar, we'll process the single file.
                    base_dir = os.path.dirname(file_path)

                # This variable is used in process_import_specification_from_local but was not defined
                full_path = temp_dir

                close_old_connections()
                created_count = process_import_specification_from_local(
                    project=project,
                    full_path=full_path,
                    base_dir=base_dir,
                    current_version=current_version,
                    user=user,
                )

                active_users = User.objects.filter(is_active=True)
                notifications = [
                    NotificationModel(
                        user=u,
                        title="Local Folder Import Successful",
                        message=f"Successfully synced and created {created_count} new specifications from local folder for project '{project.name}'."
                    ) for u in active_users
                ]
                NotificationModel.objects.bulk_create(notifications)
                print(f"Successfully synced and created {created_count} new specifications from local folder for project '{project.name}'.")
            except Exception as e:
                print(f"Failed to access local folder: {e}")
                NotificationModel.objects.create(
                    user=user,
                    title="Local Folder Import Failed",
                    message=f"Failed to sync specifications from local folder for project '{project.name}'. Error: {str(e)}"
                )
            finally:
                close_old_connections()
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                        print(f"Successfully cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"Error cleaning up temporary directory {temp_dir}: {e}")

        thread = threading.Thread(
            target=run_local_import, args=(project, file_path, temp_dir, current_version, request.user)
        )
        thread.start()

        return Response(
            {
                "message": "Local folder import has been started in the background. You will be notified upon completion."
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def import_specification_from_local_folder(self, request):
        """
        Recursively syncs local .md files to the project specifications.
        Expects 'project' in request data and optional 'path' in query params.
        """
        base_dir = request.data.get("local_folder")
        current_version = request.data.get("version")
        project_id = request.data.get("project_id")
        
        # Check if project_id is provided
        if not project_id:
            return Response(
                {"error": "project is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = ProjectModel.objects.get(id=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        
        # Check if base_dir is provided in request data or fallback to environment variable
        if not base_dir:
            return Response(
                {"error": "The import folder path is not configured. Please set the 'local_folder' in the request data."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        full_path = os.path.abspath(base_dir)

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        def run_local_import(project, full_path, base_dir, current_version, user):
            try:
                close_old_connections()
                created_count = process_import_specification_from_local(
                    project=project,
                    full_path=full_path,
                    base_dir=base_dir,
                    current_version=current_version,
                    user=user,
                )

                active_users = User.objects.filter(is_active=True)
                notifications = [
                    NotificationModel(
                        user=u,
                        title="Local Folder Import Successful",
                        message=f"Successfully synced and created {created_count} new specifications from local folder for project '{project.name}'."
                    ) for u in active_users
                ]
                NotificationModel.objects.bulk_create(notifications)
                print(f"Successfully synced and created {created_count} new specifications from local folder for project '{project.name}'.")
            except Exception as e:
                print(f"Failed to access local folder: {e}")
                NotificationModel.objects.create(
                    user=user,
                    title="Local Folder Import Failed",
                    message=f"Failed to sync specifications from local folder for project '{project.name}'. Error: {str(e)}"
                )
            finally:
                close_old_connections()

        thread = threading.Thread(
            target=run_local_import, args=(project, full_path, base_dir, current_version, request.user)
        )
        thread.start()

        return Response(
            {
                "message": "Local folder import has been started in the background. You will be notified upon completion."
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def import_specification_from_google_drive(self, request):
        """
        Fetch a Google Drive folder tree recursively and sync changes to project specifications.
        Expects 'project_id' and 'folder_id' in request data.
        """
        project_id = request.data.get("project_id")
        google_drive_url = request.data.get("google_drive_url")
        folder_id = request.data.get("folder_id")

        # Extract folder ID if a full Google Drive URL is provided
        url_to_parse = google_drive_url or folder_id
        if url_to_parse and "drive.google.com" in url_to_parse:
            match = re.search(r"(?:folders/|id=)([a-zA-Z0-9-_]+)", url_to_parse)
            if match:
                folder_id = match.group(1)

        current_version = request.data.get("version")
        previous_version = None
        if not project_id or not folder_id:
            return Response(
                {"error": "Both 'project_id' and 'folder_id' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = ProjectModel.objects.get(pk=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        def run_google_drive_import(project, folder_id, current_version, user):
            try:
                # Clean up any stale connections in the thread
                close_old_connections()
                created_count = process_import_specification_from_google_drive(
                    project=project,
                    folder_id=folder_id,
                    current_version=current_version,
                    user=user,
                )

                active_users = User.objects.filter(is_active=True)
                notifications = [
                    NotificationModel(
                        user=u,
                        title="Google Drive Import Successful",
                        message=f"Successfully synced and created {created_count} new specifications from Google Drive for project '{project.name}'."
                    ) for u in active_users
                ]
                NotificationModel.objects.bulk_create(notifications)
                print(f"Successfully synced and created {created_count} new specifications from Google Drive for project '{project.name}'.")
            except Exception as e:
                print(f"Failed to access Google Drive: {e}")
                NotificationModel.objects.create(
                    user=user,
                    title="Google Drive Import Failed",
                    message=f"Failed to sync specifications from Google Drive for project '{project.name}'. Error: {str(e)}"
                )
            finally:
                close_old_connections()

        thread = threading.Thread(
            target=run_google_drive_import, args=(project, folder_id, current_version, request.user)
        )
        thread.start()

        return Response(
            {
                "message": "Google Drive import has been started in the background. You will be notified upon completion."
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def import_specification_from_github(self, request):
        """
        Fetch the GitHub tree, parse it, and generate change summaries.
        Expects 'project' in request data.
        """
        project_id = request.data.get("project_id")
        github_url = request.data.get("github_url")
        folder_id = request.data.get("folder_id")
        owner = None
        repo = None
        branch = None
        url_to_parse = github_url or folder_id
        # Extract GitHub owner, repo, and branch if a full GitHub URL is provided
        if url_to_parse and "github.com" in url_to_parse:
            match = re.search(
                r"github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+))?", url_to_parse
            )
            if match:
                owner = match.group(1)
                repo = match.group(2).replace(".git", "")
                branch = match.group(3)

        version = request.data.get("version")
        github_token = get_github_app_installation_token()

        try:
            project = ProjectModel.objects.get(pk=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        def run_github_import(branch, github_token, owner, project, repo, user, version):
            try:
                close_old_connections()
                result = process_import_specification_from_github(
                    branch=branch,
                    github_token=github_token,
                    owner=owner,
                    project=project,
                    repo=repo,
                    user=user,
                    version=version,
                )
                if isinstance(result, Response):
                    error_msg = result.data.get("error", "Unknown error") if hasattr(result, "data") else "Unknown error"
                    raise Exception(error_msg)

                created_count = result
                active_users = User.objects.filter(is_active=True)
                notifications = [
                    NotificationModel(
                        user=u,
                        title="GitHub Import Successful",
                        message=f"Successfully synced and created {created_count} new specifications from GitHub for project '{project.name}'."
                    ) for u in active_users
                ]
                NotificationModel.objects.bulk_create(notifications)
                print(f"Successfully synced and created {created_count} new specifications from GitHub for project '{project.name}'.")
            except Exception as e:
                print(f"Failed to access GitHub: {e}")
                NotificationModel.objects.create(
                    user=user,
                    title="GitHub Import Failed",
                    message=f"Failed to sync specifications from GitHub for project '{project.name}'. Error: {str(e)}"
                )
            finally:
                close_old_connections()

        thread = threading.Thread(
            target=run_github_import, args=(branch, github_token, owner, project, repo, request.user, version)
        )
        thread.start()

        return Response(
            {
                "message": "GitHub import has been started in the background. You will be notified upon completion."
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"])
    def import_specification_from_jama(self, request):
        """
        Fetch the JAMA items, parse it, and generate change summaries.
        Expects 'project' in request data.
        """
        project_id = request.data.get("project_id")
        jama_project_id = request.data.get("jama_project_id")
        jama_url = request.data.get("jama_url")
        version = request.data.get("version")
        client_id="vz8jngyfekaygcy"
        client_secret="18ao6z4p2lq0hzlvlezr7jnqt"

        try:
            project = ProjectModel.objects.get(pk=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        def run_jama_import(project, jama_url, jama_project_id, version, client_id, client_secret, user):
            try:
                close_old_connections()
                result = process_import_specification_from_jama(
                    project,
                    jama_url=jama_url,
                    jama_project_id=jama_project_id,
                    version=version,
                    client_id=client_id,
                    client_secret=client_secret,
                    user=user,
                )
                if isinstance(result, Response):
                    error_msg = result.data.get("error", "Unknown error") if hasattr(result, "data") else "Unknown error"
                    raise Exception(error_msg)

                created_count = result
                active_users = User.objects.filter(is_active=True)
                notifications = [
                    NotificationModel(
                        user=u,
                        title="JAMA Import Successful",
                        message=f"Successfully synced and created {created_count} new specifications from JAMA for project '{project.name}'."
                    ) for u in active_users
                ]
                NotificationModel.objects.bulk_create(notifications)
                print(f"Successfully synced and created {created_count} new specifications from JAMA for project '{project.name}'.")
            except Exception as e:
                print(f"Failed to access JAMA: {e}")
                NotificationModel.objects.create(
                    user=user,
                    title="JAMA Import Failed",
                    message=f"Failed to sync specifications from JAMA for project '{project.name}'. Error: {str(e)}"
                )
            finally:
                close_old_connections()

        thread = threading.Thread(
            target=run_jama_import, args=(project, jama_url, jama_project_id, version, client_id, client_secret, request.user)
        )
        thread.start()

        return Response(
            {
                "message": "GitHub import has been started in the background. You will be notified upon completion."
            },
            status=status.HTTP_202_ACCEPTED,
        )
