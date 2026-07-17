import requests
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from specification_centralized_spec.apps import SpecificationCentralizedSpecConfig

class LucidchartViewSet(viewsets.ViewSet):
    """
    API endpoint that allows interaction with the Lucidchart API.
    """

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def export(self, request):
        """
        Export a Lucidchart diagram to JSON.
        Expects 'document_id' and optional 'page_id' or 'page_title' in query params.
        """
        document_id = request.query_params.get("document_id")
        page_id = request.query_params.get("page_id")
        page_title = request.query_params.get("page_title")
        if not document_id:
            return Response(
                {"error": "Parameter 'document_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lucidchart_token = getattr(SpecificationCentralizedSpecConfig, "LUCIDCHART_TOKEN", None)
        if not lucidchart_token:
            return Response(
                {"error": "Server configuration error: LUCIDCHART_TOKEN not found."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        url = f"https://api.lucid.co/documents/{document_id}/contents"
        headers = {
            "Authorization": f"Bearer {lucidchart_token}",
            "Accept": "application/json",
            "Lucid-Api-Version": "1",
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 403:
                return Response(
                    {"error": "Forbidden: You do not have access to this document."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if response.status_code == 404:
                return Response(
                    {"error": "Document not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            response.raise_for_status()
            
            data = response.json()
            
            if page_id and "pages" in data:
                data["pages"] = [page for page in data["pages"] if str(page.get("id")) == str(page_id)]
                if not data["pages"]:
                    return Response(
                        {"error": f"Page with ID '{page_id}' not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            elif page_title and "pages" in data:
                data["pages"] = [page for page in data["pages"] if page.get("title") == page_title]
                if not data["pages"]:
                    return Response(
                        {"error": f"Page with title '{page_title}' not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(data, status=status.HTTP_200_OK)
        except requests.RequestException as e:
            return Response(
                {"error": f"Lucidchart API call failed: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )