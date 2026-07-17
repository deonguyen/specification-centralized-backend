from specification_centralized_core.models.specification_model import SpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.serializers.specification_serializer import SpecificationSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class SpecificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows specifications to be viewed or edited.
    """

    queryset = SpecificationModel.objects.all().order_by("-id")
    serializer_class = SpecificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = [
        "project_id",
        "code",
        "name",
        "status",
        "type",
        "version",
        "source",
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        project_id = request.query_params.get("project_id")
        code = request.query_params.get("code")
        name = request.query_params.get("name")

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if code:
            queryset = queryset.filter(code__icontains=code)
        if name:
            queryset = queryset.filter(name__icontains=name)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
 
        for item in data:
            latest_revision = SpecificationRevisionModel.objects.filter(
                specification_id=item.get("id")
            ).order_by("-change_date").first()
            item["specification_revision_change_summary"] = (
                latest_revision.change_summary if latest_revision else None
            )

        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    @action(detail=False, methods=["get"])
    def get_specification_by_sql(self, request):
        """
        Custom action to get specification data using a raw SQL query.
        """
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response(
                {"error": "The 'project_id' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.db import connection
            import os

            sql_file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "sql_queries",
                "specification_query.sql",
            )
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_query = f.read()

            sql_query = sql_query.strip().rstrip(";")
            wrapped_query = f"SELECT * FROM ({sql_query}) AS subquery WHERE 1=1"
            params = []

            wrapped_query += " AND project_id = %s"
            params.append(project_id)

            category1 = request.query_params.get("category1")
            component_name = request.query_params.get("component_name")
            function_name = request.query_params.get("function_name")
            specification_name = request.query_params.get("specification_name")
            specification_type = request.query_params.get("specification_type")
            specification_version = request.query_params.get("specification_version")

            if category1:
                wrapped_query += " AND category1 = %s"
                params.append(category1)
            if component_name:
                wrapped_query += " AND component_name = %s"
                params.append(component_name)
            if function_name:
                wrapped_query += " AND function_name = %s"
                params.append(function_name)
            if specification_name:
                wrapped_query += " AND specification_name LIKE %s"
                params.append(f"{specification_name}%")
            if specification_type:
                wrapped_query += " AND specification_type = %s"
                params.append(specification_type)
            if specification_version:
                wrapped_query += " AND specification_version = %s"
                params.append(specification_version)

            with connection.cursor() as cursor:
                cursor.execute(wrapped_query, params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(results, request)
            if page is not None:
                return paginator.get_paginated_response(page)

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def get_jama_specification_hierarchy(self, request):
        """
        Custom action to get specification hierarchy from a JSON file.
        """
        try:
            import os
            import json

            json_file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "abstract_items_result.json",
            )
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            items = {
                item["id"]: item for item in data if item.get("type") == "items"
            }
            
            children_map = {}
            root_items = []

            for item_id, item in items.items():
                parent_info = item.get("location", {}).get("parent", {})
                parent_id = parent_info.get("item")
                if parent_id:
                    if parent_id not in children_map:
                        children_map[parent_id] = []
                    children_map[parent_id].append(item)
                elif "project" in parent_info:
                    root_items.append(item)

            def build_hierarchy(item_list):
                hierarchy = []
                for item in item_list:
                    node = {
                        "id": item.get("id"),
                        "documentKey": item.get("documentKey"),
                        "globalId": item.get("globalId"),
                        "name": item.get("fields", {}).get("name"),
                        "children": build_hierarchy(children_map.get(item["id"], [])),
                    }
                    hierarchy.append(node)
                return hierarchy

            result = build_hierarchy(root_items)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )