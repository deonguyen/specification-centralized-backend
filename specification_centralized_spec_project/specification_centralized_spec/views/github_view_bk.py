from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.services import github_service
from specification_centralized_spec.services.github_app_service import get_github_app_installation_token
from specification_centralized_spec.views.vertex_ai_view import VertexAIView
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import json
import re
import requests


class GitHubViewSet(viewsets.ViewSet):
    """
    API endpoint that allows interaction with the GitHub API.
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request) -> Response:
        """
        List repositories from GitHub for the authenticated user.
        Requires GITHUB_TOKEN to be set in environment variables.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Endpoint to fetch repositories for the authenticated user
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """
        Fetch the recursive tree structure of a GitHub repository.
        Expects 'owner', 'repo', and optionally 'branch' (default: main) in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        branch = SpecificationCentralizedSpecConfig.GITHUB_BRANCH

        if not owner or not repo:
            return Response(
                {"error": "Parameters 'owner' and 'repo' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # GitHub API to get the tree recursively
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return Response(
                    {"error": "Repository or branch not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def commits(self, request):
        """
        Fetch the last two commits of a branch from a GitHub repository.
        Expects an optional 'branch' in query params, otherwise defaults to server config.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        branch = SpecificationCentralizedSpecConfig.GITHUB_BRANCH

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"sha": branch}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return Response(
                    {"error": "Repository or branch not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def lasttwocommits(self, request):
        """
        Fetch the last two commits of a branch from a GitHub repository.
        Expects an optional 'branch' in query params, otherwise defaults to server config.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        branch = SpecificationCentralizedSpecConfig.GITHUB_BRANCH

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"sha": branch, "per_page": 2}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return Response(
                    {"error": "Repository or branch not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def pullrequests(self, request):
        """
        Fetch all pull requests for a branch from a GitHub repository.
        Expects an optional 'branch' in query params, otherwise defaults to server config.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        branch = request.query_params.get("branch") or SpecificationCentralizedSpecConfig.GITHUB_BRANCH

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"base": branch, "state": "all"}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return Response(
                    {"error": "Repository not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def pullrequestcomments(self, request):
        """
        Fetch all comments for a specific pull request from a GitHub repository.
        Expects 'pull_number' in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        pull_number = request.query_params.get("pull_number")

        if not owner or not repo:
            return Response(
                {"error": "Server configuration for GitHub owner and repo is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not pull_number:
            return Response(
                {"error": "Parameter 'pull_number' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # General PR conversation comments are "issue comments", code review comments are "pulls comments"
        issue_comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
        review_comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/comments"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            issue_response = requests.get(issue_comments_url, headers=headers)
            if issue_response.status_code == 404:
                return Response({"error": "Pull request not found."}, status=status.HTTP_404_NOT_FOUND)
            issue_response.raise_for_status()
            
            review_response = requests.get(review_comments_url, headers=headers)
            review_response.raise_for_status()
            
            all_comments = issue_response.json() + review_response.json()
            
            # Sort combined comments chronologically
            all_comments.sort(key=lambda x: x.get("created_at", ""))

            return Response(all_comments, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def filecontent(self, request):
        """
        Fetch the content of a file from GitHub using its SHA.
        Expects 'sha' in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        sha = request.query_params.get("sha")

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not sha:
            return Response(
                {"error": "Parameter 'sha' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/git/blobs/{sha}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return Response(
                    {"error": "File content not found for the given SHA."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def treewithsha(self, request):
        """
        Fetch the recursive tree structure of a GitHub repository using a SHA.
        Expects 'sha' in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        sha = request.query_params.get("sha")

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not sha:
            return Response(
                {"error": "Parameter 'sha' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}?recursive=1"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return Response(
                    {"error": "Tree not found for the given SHA."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def filecontentwithref(self, request):
        """
        Fetch the content of a file from GitHub using a file path and a reference (branch or commit SHA).
        Expects 'path' and 'ref' in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        path = request.query_params.get("path")
        ref = request.query_params.get("ref")

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not path or not ref:
            return Response(
                {"error": "Parameters 'path' and 'ref' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"ref": ref}

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return Response(
                    {"error": "File or reference not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["post"])
    def synctree(self, request):
        """
        Fetch the GitHub tree, parse it, and generate change summaries.
        Expects 'project' in request data.
        """
        project = request.data.get("project")
        if not project:
            return Response(
                {"error": "project is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = ProjectModel.objects.get(pk=project)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
            project=project,
            category1="root",
            category2="root",
            defaults={"specification_order": 0},
        )

        latest_commit_sha = None
        previous_commit_sha = None

        last_two_commits_response = self.lasttwocommits(request)
        if last_two_commits_response.status_code == status.HTTP_200_OK:
            commits = last_two_commits_response.data
            if len(commits) > 0:
                latest_commit_sha = commits[0].get("sha")
            if len(commits) > 1:
                previous_commit_sha = commits[1].get("sha")

        tree_response = self.tree(request)
        if tree_response.status_code != 200:
            return tree_response

        tree_data = tree_response.data.get("tree", [])
        tree_data.sort(key=lambda x: x.get("path", "").count("/"))

        path_to_spec = {"": root_spec}
        created_count = 0
        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        github_token = get_github_app_installation_token()

        for item in tree_data:
            path = item.get("path", "")
            item_type = item.get("type", "")

            if not path or path.endswith("README.md"):
                continue

            change_summary = ""
            if item_type == "blob" and latest_commit_sha and previous_commit_sha:
                previous_content = self._get_file_content_base64(
                    owner, repo, path, github_token, previous_commit_sha
                )
                latest_content = self._get_file_content_base64(
                    owner, repo, path, github_token, latest_commit_sha
                )
                if latest_content is None and previous_content is None:
                    pass
                elif latest_content is not None and previous_content is None:
                    change_summary = "Add new document content"
                elif latest_content != previous_content:
                    change_summary = VertexAIView().get_diff_summary(
                        previous_content, latest_content
                    )

            parts = path.split("/")
            name = parts[-1]
            parent_path = "/".join(parts[:-1])
            parent_spec = path_to_spec.get(parent_path, root_spec)

            spec_obj, _ = SpecificationModel.objects.update_or_create(
                name=name,
                code=name,
                defaults={
                    "source": "GitHub",
                    "status": "draft",
                    "type": item_type,
                },
            )

            spec, created = ProjectSpecificationModel.objects.update_or_create(
                project=project,
                specification=spec_obj,
                defaults={
                    "parent": parent_spec,
                    "category1": "",
                    "category2": "",
                },
            )

            if created:
                created_count += 1

            if change_summary:
                SpecificationRevisionModel.objects.update_or_create(
                    specification=spec_obj,
                    version=latest_commit_sha or "",
                    defaults={
                        "updated_by": request.user,
                        "previous_version": previous_commit_sha or "",
                        "change_summary": change_summary,
                    },
                )

            if item_type == "tree":
                path_to_spec[path] = spec

        return Response(
            {
                "message": f"Successfully synced and created {created_count} new specifications."
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def synctree1(self, request):
        """
        Fetch the GitHub tree, parse it, and generate change summaries.
        Expects 'project' in request data.
        """
        project = request.data.get("project")
        if not project:
            return Response(
                {"error": "project is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = ProjectModel.objects.get(pk=project)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        root_spec, _ = ProjectSpecificationModel.objects.get_or_create(
            project=project,
            category1="root",
            category2="root",
            defaults={"specification_order": 0},
        )

        commits_sha = []
        commits_response = self.commits(request)
        if commits_response.status_code != 200:
            return commits_response

        # loop by index and accumulate SHAs
        for i in range(len(commits_response.data)):
            commit = commits_response.data[i]
            if isinstance(commit, dict):
                sha = commit.get("sha")
                if sha:
                    commits_sha.append(sha)
        commits_sha.reverse()

        previous_commit_sha = None
        latest_commit_sha = None

        tree_response = self.tree(request)
        if tree_response.status_code != 200:
            return tree_response

        tree_data = tree_response.data.get("tree", [])
        tree_data.sort(key=lambda x: x.get("path", "").count("/"))

        path_to_spec = {"": root_spec}
        created_count = 0
        owner = SpecificationCentralizedSpecConfig.GITHUB_OWNER
        repo = SpecificationCentralizedSpecConfig.GITHUB_REPO
        github_token = get_github_app_installation_token()

        for item in tree_data:
            path = item.get("path", "")
            item_type = item.get("type", "")

            if not path or path.endswith("README.md"):
                continue

            commits_sha_length = len(commits_sha)
            previous_commit_sha = None
            latest_commit_sha = None
            for i in range(commits_sha_length - 1):

                previous_commit_sha = commits_sha[i]
                latest_commit_sha = commits_sha[i + 1]

                change_summary = ""
                if item_type == "blob" and latest_commit_sha and previous_commit_sha:
                    previous_content = self._get_file_content_base64(
                        owner, repo, path, github_token, previous_commit_sha
                    )
                    latest_content = self._get_file_content_base64(
                        owner, repo, path, github_token, latest_commit_sha
                    )

                    if latest_content is None and previous_content is None:
                        pass
                    elif latest_content is not None and previous_content is None:
                        change_summary = "Add new document content"
                    elif latest_content != previous_content:
                        change_summary = VertexAIView().get_diff_summary(
                            previous_content, latest_content
                        )

                    parts = path.split("/")
                    name = parts[-1]
                    parent_path = "/".join(parts[:-1])
                    parent_spec = path_to_spec.get(parent_path, root_spec)

                    spec_obj, _ = SpecificationModel.objects.update_or_create(
                        name=name,
                        code=name,
                        defaults={
                            "source": "GitHub",
                            "status": "draft",
                            "type": item_type,
                        },
                    )

                    spec, created = ProjectSpecificationModel.objects.update_or_create(
                        project=project,
                        specification=spec_obj,
                        defaults={
                            "parent": parent_spec,
                            "category1": "",
                            "category2": "",
                        },
                    )

                    if created:
                        created_count += 1

                    if change_summary:
                        SpecificationRevisionModel.objects.update_or_create(
                            specification=spec_obj,
                            version=latest_commit_sha or "",
                            defaults={
                                "updated_by": request.user,
                                "previous_version": previous_commit_sha or "",
                                "change_summary": change_summary,
                            },
                        )

                    if item_type == "tree":
                        path_to_spec[path] = spec

        return Response(
            {
                "message": f"Successfully synced and created {created_count} new specifications."
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def organizehierarchy(self, request):
        """
        Fetch the GitHub tree, parse it, and use Vertex AI to determine document hierarchy.
        Expects 'project' in request data.
        """
        project = request.data.get("project")
        if not project:
            return Response(
                {"error": "project is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = ProjectModel.objects.get(pk=project)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        tree_response = self.tree(request)
        if tree_response.status_code != 200:
            return tree_response

        tree_data = tree_response.data.get("tree", [])
        file_paths = [
            item.get("path")
            for item in tree_data
            if item.get("type") == "blob"
            and not item.get("path", "").endswith("README.md")
        ]

        if not file_paths:
            return Response(
                {"message": "No files found to organize."}, status=status.HTTP_200_OK
            )

        vertex_view = VertexAIView()
        ai_response = vertex_view.get_document_hierarchy(file_paths)

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
        for child_path, parent_path in hierarchy.items():
            if not parent_path:
                continue

            child_name = child_path.split("/")[-1]
            parent_name = parent_path.split("/")[-1]

            child_spec = ProjectSpecificationModel.objects.filter(
                project=project, category1=child_name
            ).first()
            parent_spec = ProjectSpecificationModel.objects.filter(
                project=project, category1=parent_name
            ).first()

            if child_spec and parent_spec and child_spec != parent_spec:
                child_spec.parent = parent_spec
                child_spec.save()
                updated_count += 1

        return Response(
            {
                "message": f"Successfully updated {updated_count} hierarchy relationships."
            },
            status=status.HTTP_200_OK,
        )

    def _get_file_content_base64(self, owner, repo, path, github_token, ref):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {"Authorization": f"token {github_token}"}
        params = {"ref": ref}
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            response_json = response.json()
            content_b64 = (
                response_json.get("content")
                if isinstance(response_json, dict)
                else None
            )
            return content_b64
        except requests.RequestException:
            return None
        return None
    
    @action(detail=False, methods=["get"])
    def search_swrd_in_repos(self, request):
        """
        Recursively search all files from a GitHub repository for text beginning with 'swrd_'.
        Expects optional 'sha', 'branch', and 'search' in query params.
        """
        github_token = getattr(SpecificationCentralizedSpecConfig, "GITHUB_TOKEN", None)
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = getattr(SpecificationCentralizedSpecConfig, "GITHUB_OWNER", None)
        repo = getattr(SpecificationCentralizedSpecConfig, "GITHUB_REPO", None)
        ref = (
            request.query_params.get("sha")
            or request.query_params.get("branch")
            or getattr(SpecificationCentralizedSpecConfig, "GITHUB_BRANCH", "dev")
        )
        search_prefix = request.query_params.get("search", "swrd_")

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            results = github_service.search_text_recursive(
                github_token, owner, repo, "", ref, search_prefix
            )
            return Response(results, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["get"])
    def search_swrd_in_prs(self, request):
        """
        Fetch all pull requests for a branch/sha and search their comments for a prefix.
        Expects optional 'sha', 'branch', and 'search' in query params.
        """
        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GITHUB_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        owner = getattr(SpecificationCentralizedSpecConfig, "GITHUB_OWNER", None)
        repo = getattr(SpecificationCentralizedSpecConfig, "GITHUB_REPO", None)
        ref = (
            request.query_params.get("sha")
            or request.query_params.get("branch")
            or getattr(SpecificationCentralizedSpecConfig, "GITHUB_BRANCH", "dev")
        )
        search_prefix = request.query_params.get("search", "swrd_")

        if not owner or not repo:
            return Response(
                {
                    "error": "Server configuration for GitHub owner and repo is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {"base": ref, "state": "all"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            pulls = response.json()

            results = []
            pattern = re.compile(rf"\b{re.escape(search_prefix)}\w*", re.IGNORECASE)

            for pr in pulls:
                pr_number = pr.get("number")
                if not pr_number:
                    continue

                # Fetch issue comments (general PR comments)
                issue_comments_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
                issue_resp = requests.get(issue_comments_url, headers=headers)

                # Fetch PR review comments
                review_comments_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
                review_resp = requests.get(review_comments_url, headers=headers)

                comments = []
                if issue_resp.status_code == 200:
                    comments.extend(issue_resp.json())
                if review_resp.status_code == 200:
                    comments.extend(review_resp.json())

                pr_matches = set()
                for comment in comments:
                    body = comment.get("body")
                    if body:
                        matches = pattern.findall(body)
                        pr_matches.update(matches)

                if pr_matches:
                    results.append(
                        {
                            "pull_number": pr_number,
                            "title": pr.get("title"),
                            "html_url": pr.get("html_url"),
                            "matches": list(pr_matches),
                        }
                    )

            return Response(results, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )