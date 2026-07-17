from django.conf import settings
from specification_centralized_core.models import ProjectModel, ProjectSpecificationModel

from specification_centralized_spec.services.import_specification_service import process_import_specification_from_local
from specification_centralized_spec.views.vertex_ai_view import VertexAIView
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json
import os
import re
import strip_markdown


class LocalFileViewSet(viewsets.ViewSet):
    """
    API endpoint for interacting with local files.
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def content(self, request):
        """
        Fetches the content of a local file.
        Expects 'path' in query params.
        The path is relative to a pre-configured base directory for security.
        """
        # Define a base directory to prevent access to arbitrary files.
        # This must be configured in your Django settings.py
        base_dir = getattr(settings, "LOCAL_FILE_BASE_DIR", None)
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path")
        if not file_path_relative:
            return Response(
                {"error": "Parameter 'path' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Securely construct the full path and prevent directory traversal.
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        # Check that the resolved path is within the configured base directory.
        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.isfile(full_path):
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            return Response(
                {"path": file_path_relative, "content": content},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to read file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def bulletin(self, request):
        """
        Fetches the content of a local file and generates a bulleted summary using Vertex AI.
        Expects 'path' in query params.
        """

        file_path = request.data.get("file_path")
        if not file_path:
            return Response(
                {"error": "Parameter 'path' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.isfile(file_path):
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            vertex_view = VertexAIView()
            bulletin = vertex_view.get_document_bulletin(content)

            return Response(
                {"path": file_path, "bulletin": bulletin},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to generate bulletin: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def bulletinitemcontent(self, request):
        """
        Fetches the content of a local file and extracts detailed content for a specific bulletin item using Vertex AI.
        Expects 'path' in query params and 'bulletin_item' in request data.
        """
        file_path = request.data.get("file_path")
        bulletin_item = request.data.get("bulletin_item")

        if not os.path.isfile(file_path):
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            vertex_view = VertexAIView()
            detailed_content = vertex_view.get_bulletin_item_content(
                content, bulletin_item
            )

            return Response(
                {
                    "path": file_path,
                    "bulletin_item": bulletin_item,
                    "content": detailed_content,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to extract content: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def comparelocalfile(self, request):
        """
        Fetches the content of a local file and extracts detailed content for a specific bulletin item using Vertex AI.
        Expects 'path' in query params and 'bulletin_item' in request data.
        """
        file_path1 = request.data.get("file_path1")
        file_path2 = request.data.get("file_path2")

        if not os.path.isfile(file_path1) or not os.path.isfile(file_path2):
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            with open(file_path1, "r", encoding="utf-8") as f:
                content1 = f.read()

            with open(file_path2, "r", encoding="utf-8") as f:
                content2 = f.read()

            vertex_view = VertexAIView()
            diff_content = vertex_view.get_diff_summary(content1, content2)

            return Response(
                {
                    "path1": file_path1,
                    "path2": file_path2,
                    "content": diff_content,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to extract content: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Recursively fetches all files and directories starting from a given path.
        Expects optional 'path' in query params.
        """
        base_dir = getattr(settings, "LOCAL_FILE_BASE_DIR", None)
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path", "")

        # Securely construct the full path and prevent directory traversal.
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        # Check that the resolved path is within the configured base directory.
        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        tree_data = []
        for root, dirs, files in os.walk(full_path):
            for name in dirs:
                rel_path = os.path.relpath(os.path.join(root, name), base_dir).replace(
                    os.sep, "/"
                )
                tree_data.append({"path": rel_path, "type": "tree"})
            for name in files:
                rel_path = os.path.relpath(os.path.join(root, name), base_dir).replace(
                    os.sep, "/"
                )
                tree_data.append({"path": rel_path, "type": "blob"})

        return Response({"tree": tree_data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def synclocal(self, request):
        """
        Recursively syncs local .md files to the project specifications.
        Expects 'project' in request data and optional 'path' in query params.
        """
        project_id = request.data.get("project_id")
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

        base_dir = request.data.get("local_folder")
        current_version = request.data.get("version")
        previous_version = None
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path", "")
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        created_count = process_import_specification_from_local(
            project=project,
            full_path=full_path,
            base_dir=base_dir,
            current_version=current_version,
            user=request.user,
        )

        return Response(
            {
                "message": f"Successfully synced and created {created_count} new specifications."
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def search_swrd(self, request):
        """
        Recursively search all files from a local directory for text beginning with a prefix (default: 'swrd_').
        Expects optional 'path' and 'search' in query params.
        """
        base_dir = getattr(settings, "LOCAL_FILE_BASE_DIR", None)
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path", "")
        search_prefix = request.query_params.get("search", "swrd_")

        # Securely construct the full path and prevent directory traversal.
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        # Check that the resolved path is within the configured base directory.
        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        results = []
        # Matches a word boundary followed by the target prefix and any subsequent word characters
        pattern = re.compile(rf"\b{re.escape(search_prefix)}\w*", re.IGNORECASE)

        for root, dirs, files in os.walk(full_path):
            for name in files:
                f_path = os.path.join(root, name)
                try:
                    with open(f_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        matches = list(set(pattern.findall(content)))
                        if matches:
                            rel_path = os.path.relpath(f_path, base_dir).replace(os.sep, "/")
                            results.append({
                                "path": rel_path,
                                "matches": matches
                            })
                except (UnicodeDecodeError, IOError):
                    # Skip binary files or files that cannot be read as UTF-8
                    pass

        return Response(results, status=status.HTTP_200_OK)

    def _find_spec_by_path(self, project, path, root_spec):
        """
        Finds a ProjectSpecification object by traversing the hierarchy based on its path.
        """
        parts = path.split("/")
        current_spec = root_spec
        for part in parts:
            if not part:
                continue
            try:
                # This assumes (parent, category1) is unique for a project, which synclocal should ensure.
                current_spec = ProjectSpecificationModel.objects.get(
                    project=project, parent=current_spec, category1=""
                )
            except ProjectSpecificationModel.DoesNotExist:
                # Can't find a part of the path, so the full path doesn't exist.
                return None
            except ProjectSpecificationModel.MultipleObjectsReturned:
                # This indicates a data integrity issue. The combination of parent and name should be unique.
                return None
        return current_spec

    @action(detail=False, methods=["post"])
    def organizehierarchy(self, request):
        """
        Recursively finds all .md files, and uses Vertex AI to determine document hierarchy.
        Expects 'project' in request data and optional 'path' in query params.
        """
        project_id = request.data.get("project_id")
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

        base_dir = "C:\\WovenbyToyota\\bev_document-vf.v1.4.0\\"
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path", "")
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        md_files = []
        for root, _, files in os.walk(full_path):
            for name in files:
                if name.endswith(".md"):
                    f_path = os.path.join(root, name)
                    rel_path = os.path.relpath(f_path, base_dir).replace(os.sep, "/")
                    md_files.append(rel_path)

        if not md_files:
            return Response(
                {"message": "No .md files found to organize."},
                status=status.HTTP_200_OK,
            )

        vertex_view = VertexAIView()
        ai_response = vertex_view.get_document_hierarchy(md_files)

        hierarchy = {}
        try:
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", ai_response, re.DOTALL)
            json_str = json_match.group(1) if json_match else ai_response
            if not json_match:
                json_match = re.search(r"(\{.*\})", ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
            hierarchy = json.loads(json_str)
        except Exception:
            return Response(
                {
                    "error": "Failed to parse AI hierarchy response.",
                    "details": ai_response,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        updated_count = 0
        try:
            root_spec = ProjectSpecificationModel.objects.get(
                project=project, category1="root", category2="root"
            )
        except ProjectSpecificationModel.DoesNotExist:
            return Response(
                {"error": "Project root not found. Please sync the project first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ProjectSpecificationModel.MultipleObjectsReturned:
            return Response(
                {"error": "Multiple project roots found. Data integrity issue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        for child_path, parent_path in hierarchy.items():
            child_spec = self._find_spec_by_path(project, child_path, root_spec)

            if not child_spec:
                continue

            if parent_path:
                parent_spec = self._find_spec_by_path(project, parent_path, root_spec)
            else:
                parent_spec = root_spec

            if not parent_spec:
                continue

            # Proceed with the update if the parent is different
            if child_spec.parent != parent_spec and child_spec != parent_spec:
                child_spec.parent = parent_spec
                child_spec.save()
                updated_count += 1

        return Response(
            {
                "message": f"Successfully updated {updated_count} hierarchy relationships."
            },
            status=status.HTTP_200_OK,
        )

    def extract_markdown_links(self, text):
        """
        Extracts all markdown links (text and URL) from a given string.

        Args:
            markdown_text: A string containing markdown content.

        Returns:
            A list of tuples, where each tuple is (link_text, url).
        """
        # Regex pattern for standard inline links targeting .md files or web links.
        # Group 1: ([^\]]+) captures the link text inside the square brackets.
        # Group 2: captures the URL inside the parentheses if it is a .md file (optionally with an anchor) or an http/https link.
        # pattern = re.compile(r'\[([^\]]+)\]\(([^)]*\.md(?:#[^)]*)?|https?://[^)]+|[a-zA-Z0-9._\-/]+\.md)\)')

        # re.findall returns a list of all non-overlapping matches of the pattern.
        # Since the pattern has two capturing groups, each match is a tuple.
        # return pattern.findall(markdown_text)
        return re.findall(r"(\/.*?\.[\w:]+)", text)

    @action(detail=False, methods=["post"])
    def gethyperlink(self, request):
        """
        Recursively syncs local .md files to the project specifications.
        Expects 'project' in request data and optional 'path' in query params.
        """
        project_id = request.data.get("project_id")
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

        base_dir = "C:\\WovenbyToyota\\bev_document-vf.v1.4.0\\"
        current_version = "1.5.0"
        previous_version = None
        if not base_dir:
            return Response(
                {"error": "Server configuration error: LOCAL_FILE_BASE_DIR not set."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        file_path_relative = request.query_params.get("path", "")
        full_path = os.path.abspath(os.path.join(base_dir, file_path_relative))

        if not full_path.startswith(os.path.abspath(base_dir)):
            return Response(
                {"error": "Invalid path. Directory traversal is not allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(full_path):
            return Response(
                {"error": "Path not found."}, status=status.HTTP_404_NOT_FOUND
            )

        root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
            project=project,
            category1="root",
            category2="root",
            defaults={"specification_order": 0},
        )

        items = []
        for root, dirs, files in os.walk(full_path):
            for name in files:
                if name.endswith(".md"):
                    f_path = os.path.join(root, name)
                    rel_path = os.path.relpath(f_path, base_dir).replace(os.sep, "/")
                    items.append(f_path)

        # items.sort(key=lambda x: x.count("/"))
        created_count = 0

        for path in items:
            with open(path, "r", encoding="utf-8") as file:
                raw_content = file.read()
                content = strip_markdown.strip_markdown(raw_content)
                lines = content.splitlines()
                for line in lines:
                    urls = self.extract_markdown_links(line)
                    if urls:
                        print(path)
                        print(urls)

        # for path in items:
        #     current_content = ""
        #     try:
        #         with open(path, "r", encoding="utf-8") as f:
        #             current_content = f.read()
        #     except Exception:
        #         pass
        #     response = self.get_url_from_text(current_content)
        #     print(response)

        # response = VertexAIView.get_document_hyperlink_and_hierarchy(self, items)
        # print(response)

        return Response(
            {
                "message": f"Successfully synced and created {created_count} new specifications."
            },
            status=status.HTTP_201_CREATED,
        )
