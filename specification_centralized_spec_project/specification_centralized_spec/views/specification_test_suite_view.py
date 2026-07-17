import os
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import django_filters
from django.db import connection

from specification_centralized_core.models.specification_test_suite_model import (
    SpecificationTestSuiteModel,
)
from specification_centralized_spec.serializers.specification_test_suite_serializer import (
    SpecificationTestSuiteSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class SpecificationTestSuiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows specification test suites to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = SpecificationTestSuiteModel.objects.all()
    serializer_class = SpecificationTestSuiteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = [
        "project_id",
        "specification_id",
        "specification_revision_id",
        "project",
        "specification",
        "specification_revision",
        "status",
        "code",
        "name",
    ]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        project_id = request.query_params.get("project_id")
        specification_id = request.query_params.get("specification_id")
        specification_revision_id = request.query_params.get(
            "specification_revision_id"
        )

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if specification_id:
            queryset = queryset.filter(specification_id=specification_id)
        if specification_revision_id:
            queryset = queryset.filter(
                specification_revision_id=specification_revision_id
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in ["project", "specification", "specification_revision"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        mutable_data = request.data.copy()

        for field in ["project", "specification", "specification_revision"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def project_specification_test_suites(self, request):
        """
        Execute the project_specification_test_suite_query.sql and return the results.
        Expects optional 'project_id' in query parameters.
        """
        sql_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "sql_queries",
            "project_specification_test_suite_query.sql",
        )

        with open(sql_file_path, "r", encoding="utf-8") as f:
            query = f.read()

        query = query.strip().rstrip(";")
        wrapped_query = f"SELECT * FROM ({query}) AS subquery WHERE 1=1"

        project_id = request.query_params.get("project_id")
        params = []
        if project_id:
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
