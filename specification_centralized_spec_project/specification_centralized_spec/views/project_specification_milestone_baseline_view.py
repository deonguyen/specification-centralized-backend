from specification_centralized_core.models.project_specification_milestone_baseline_model import (
    ProjectSpecificationMilestoneBaselineModel,
)
from specification_centralized_spec.serializers.project_specification_milestone_baseline_serializer import (
    ProjectSpecificationMilestoneBaselineSerializer,
)
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ProjectSpecificationMilestoneBaselineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project specification milestone baselines to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = ProjectSpecificationMilestoneBaselineModel.objects.all()
    serializer_class = ProjectSpecificationMilestoneBaselineSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = [
        "project_id",
        "project",
        "project_milestone",
        "project_specification",
        "specification",
        "specification_revision",
        "user",
    ]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in [
            "project",
            "project_milestone",
            "project_specification",
            "specification",
            "specification_revision",
            "user",
        ]:
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

        for field in [
            "project",
            "project_milestone",
            "project_specification",
            "specification",
            "specification_revision",
            "user",
        ]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def project_specification_milestone_baseline(self, request):
        """
        Custom action to baseline a project specification milestone.
        """
        project_id = request.data.get("project_id")
        project_milestone_id = request.data.get("project_milestone_id")
        user_id = request.data.get("user_id")
        version = request.data.get("version")

        from django.db import connection
        import os

        sql_file_path = os.path.join(os.path.dirname(__file__), "..", "sql_queries", "perform_project_specification_milestone_baseline.sql")
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_query = f.read()

        with connection.cursor() as cursor:
            cursor.execute(sql_query, [project_milestone_id, user_id, project_id, version])

        return Response({"message": "Baseline created successfully"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def get_project_specification_milestone_baseline_by_sql(self, request):
        """
        Custom action to get baseline data using a raw SQL query.
        """
        project_id = request.query_params.get("project_id")

        if not project_id:
            return Response(
                {"error": "The 'project_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.db import connection
            import os

            sql_file_path = os.path.join(os.path.dirname(__file__), "..", "sql_queries", "project_specification_milestone_baseline_query.sql")
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

    @action(detail=False, methods=["post"])
    def update_project_specification_milestone_baseline_version(self, request):
        project_id = request.data.get("project_id")
        project_specification_id = request.data.get("project_specification_id")
        milestone_id = request.data.get("milestone_id")
        version = request.data.get("version")
        user_id = request.data.get("user_id")

        try:
            from django.db import connection
            import os

            sql_file_path = os.path.join(os.path.dirname(__file__), "..", "sql_queries", "update_project_specification_milestone_baseline_version.sql")
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_query = f.read()

            with connection.cursor() as cursor:
                cursor.execute(
                    sql_query, 
                    [project_id, milestone_id, user_id, project_specification_id, version]
                )

            return Response(
                {"message": "Baseline version updated successfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )