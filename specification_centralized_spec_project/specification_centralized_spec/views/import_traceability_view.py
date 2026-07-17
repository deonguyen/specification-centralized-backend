from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from specification_centralized_core.models import (
    ProjectModel,
    ProjectSpecificationModel,
    SpecificationRevisionModel,
    CodeImplementationTraceModel,
    CodeImplementationTraceLogModel,
)
from specification_centralized_spec.services import github_service
from specification_centralized_spec.services.github_app_service import get_github_app_installation_token
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import re
import requests


class ImportTraceabilityViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["post"])
    def import_code_traceability_from_repos(self, request):
        """
        Recursively search all files from a GitHub repository for text beginning with 'swrd_'.
        Expects optional 'sha', 'branch', and 'search' in query params.
        """
        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"error": "Parameter 'project_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        try:
            project = ProjectModel.objects.get(pk=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GitHub token not available."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        ref = request.data.get("sha") or branch
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

            for item in results:
                # Exclude document files from the trace logs
                if (
                    item.get("name", "")
                    .lower()
                    .endswith((".md", ".txt", ".pdf", ".doc", ".docx"))
                ):
                    continue
                matches = item.get("matches", [])
                for match in matches:
                    project_specs = ProjectSpecificationModel.objects.filter(
                        project=project, specification__internal_id=match
                    )
                    for project_spec in project_specs:
                        latest_revision = (
                            SpecificationRevisionModel.objects.filter(
                                specification_id=project_spec.specification_id
                            )
                            .order_by("-change_date")
                            .first()
                        )
                        trace, _ = (
                            CodeImplementationTraceModel.objects.update_or_create(
                                project=project,
                                project_specification=project_spec,
                                specification=project_spec.specification,
                                defaults={
                                    "specification_revision": latest_revision,
                                    "code_implementation_status": f"draft_{project_spec.id}",
                                },
                            )
                        )
                        CodeImplementationTraceLogModel.objects.update_or_create(
                            project=project,
                            code_implementation_trace=trace,
                            path=item.get("path"),
                            name=item.get("name"),
                            defaults={
                                "sha": item.get("sha"),
                                "url": item.get("html_url") or item.get("url"),
                                "git_url": item.get("git_url"),
                                "download_url": item.get("download_url"),
                                "pull_request_sha": ref,
                            },
                        )

            return Response(results, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["post"])
    def import_code_traceability_from_prs(self, request):
        """
        Fetch all pull requests for a branch/sha and search their comments for a prefix.
        Expects optional 'sha', 'branch', and 'search' in query params.
        """
        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"error": "Parameter 'project_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project = None
        try:
            project = ProjectModel.objects.get(pk=project_id)
        except ProjectModel.DoesNotExist:
            return Response(
                {"error": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

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

        github_token = get_github_app_installation_token()
        if not github_token:
            return Response(
                {"error": "Server configuration error: GitHub token not available."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        ref = request.query_params.get("sha") or branch
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

                pr_matches = set()

                # Check PR title and body
                pr_title = pr.get("title")
                if pr_title:
                    pr_matches.update(pattern.findall(pr_title))

                pr_body = pr.get("body")
                if pr_body:
                    pr_matches.update(pattern.findall(pr_body))

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

                for comment in comments:
                    body = comment.get("body")
                    if body:
                        matches = pattern.findall(body)
                        pr_matches.update(matches)

                if pr_matches:
                    # Fetch files associated with the PR
                    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
                    files_resp = requests.get(files_url, headers=headers)
                    pr_files = []
                    if files_resp.status_code == 200:
                        pr_files = files_resp.json()

                        for file in pr_files:
                            # Exclude document files from the trace logs
                            if (
                                file.get("filename", "")
                                .lower()
                                .endswith((".md", ".txt", ".pdf", ".doc", ".docx"))
                            ):
                                continue

                            for match in pr_matches:
                                project_specs = (
                                    ProjectSpecificationModel.objects.filter(
                                        project=project,
                                        specification__internal_id=match,
                                    )
                                )
                                for project_spec in project_specs:
                                    latest_revision = (
                                        SpecificationRevisionModel.objects.filter(
                                            specification_id=project_spec.specification_id
                                        )
                                        .order_by("-change_date")
                                        .first()
                                    )
                                    trace, _ = (
                                        CodeImplementationTraceModel.objects.update_or_create(
                                            project=project,
                                            project_specification=project_spec,
                                            specification=project_spec.specification,
                                            defaults={
                                                "specification_revision": latest_revision,
                                                "code_implementation_status": f"draft_{project_spec.id}",
                                            },
                                        )
                                    )
                                    CodeImplementationTraceLogModel.objects.update_or_create(
                                        project=project,
                                        code_implementation_trace=trace,
                                        path=file.get("filename"),
                                        name=file.get("filename").split("/")[-1],
                                        defaults={
                                            "sha": file.get("sha"),
                                            "url": file.get("blob_url")
                                            or file.get("raw_url"),
                                            "git_url": file.get("contents_url"),
                                            "download_url": file.get("raw_url"),
                                            "pull_request_sha": str(pr_number),
                                        },
                                    )

                    results.append(
                        {
                            "pull_number": pr_number,
                            "title": pr.get("title"),
                            "html_url": pr.get("html_url"),
                            "matches": list(pr_matches),
                            "files": pr_files,
                        }
                    )

            return Response(results, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"GitHub API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
