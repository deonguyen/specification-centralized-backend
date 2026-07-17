from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig
from specification_centralized_core.models.project_model import ProjectModel
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.component_model import ComponentModel
from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_core.models.code_implementation_trace_model import (
    CodeImplementationTraceModel,
)
from specification_centralized_core.models.code_implementation_trace_log_model import (
    CodeImplementationTraceLogModel,
)
from specification_centralized_spec.views.vertex_ai_view import VertexAIView
from specification_centralized_spec.services.specification_service import (
    parse_specification_content,
)
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import base64
import json
import re
import requests
import markdown
from bs4 import BeautifulSoup


def tree(branch, github_token, owner, project, repo, user, version):
    """
    Fetch the recursive tree structure of a GitHub repository.
    Expects 'owner', 'repo', and optionally 'branch' (default: main) in query params.
    """
    if not github_token:
        return Response(
            {"error": "Server configuration error: GITHUB_TOKEN not found."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
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


def last_two_commits(branch, github_token, owner, project, repo, user, version):
    """
    Fetch the last two commits of a branch from a GitHub repository.
    Expects an optional 'branch' in query params, otherwise defaults to server config.
    """
    if not github_token:
        return Response(
            {"error": "Server configuration error: GITHUB_TOKEN not found."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not owner or not repo:
        return Response(
            {"error": "Server configuration for GitHub owner and repo is required."},
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


def get_file_content_base64(
    branch,
    github_token,
    owner,
    path,
    project,
    ref,
    repo,
    user,
    version,
):
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
            response_json.get("content") if isinstance(response_json, dict) else None
        )
        return content_b64
    except requests.RequestException:
        return None
    return None


def search_text_recursive(github_token, owner, repo, path, ref, search_prefix):
    """
    Helper method to recursively fetch all files and search their content for a prefix.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    params = {"ref": ref}
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 404:
        return []

    response.raise_for_status()
    items = response.json()

    if not isinstance(items, list):
        items = [items]

    results = []
    # Matches word boundary followed by the target prefix and any subsequent word characters
    pattern = re.compile(rf"\b{re.escape(search_prefix)}\w*", re.IGNORECASE)

    for item in items:
        if item.get("type") == "file":
            download_url = item.get("download_url")
            if download_url:
                content_resp = requests.get(download_url, headers=headers)
                if content_resp.status_code == 200:
                    try:
                        # Decode as UTF-8 to safely ignore binary files
                        text_content = content_resp.content.decode("utf-8")
                        matches = list(set(pattern.findall(text_content)))
                        if matches:
                            results.append(
                                {
                                    "name": item.get("name"),
                                    "path": item.get("path"),
                                    "sha": item.get("sha"),
                                    "url": item.get("url"),
                                    "html_url": item.get("html_url"),
                                    "git_url": item.get("git_url"),
                                    "download_url": item.get("download_url"),
                                    "matches": matches,
                                }
                            )
                    except UnicodeDecodeError:
                        # Skip binary or non-UTF8 files
                        pass
        elif item.get("type") == "dir":
            results.extend(
                search_text_recursive(
                    github_token, owner, repo, item.get("path"), ref, search_prefix
                )
            )

    return results
