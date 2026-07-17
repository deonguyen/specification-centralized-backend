import django_filters
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.serializers.specification_revision_serializer import (
    SpecificationRevisionSerializer,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class SpecificationRevisionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows specification revisions to be viewed or edited.
    """

    queryset = SpecificationRevisionModel.objects.all().order_by("-change_date")
    serializer_class = SpecificationRevisionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = [
        "project_id",
        "specification",
        "specification_id",
        "version",
    ]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in [
            "specification",
            "updated_by",
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
            "specification",
            "updated_by",
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

    @action(detail=False, methods=["get"])
    def first(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        item = queryset.first()
        if item:
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"])
    def distinct_version(self, request):
        """
        Custom action to get distinct versions using a raw SQL query.
        """
        try:
            from django.db import connection
            import os

            sql_file_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "sql_queries",
                "distinct_version.sql",
            )
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_query = f.read()

            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                results = [row[0] for row in cursor.fetchall()]

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
