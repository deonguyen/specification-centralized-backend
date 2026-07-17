import django_filters
from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from specification_centralized_core.models.specification_revision_model import SpecificationRevisionModel
from specification_centralized_spec.serializers.project_specification_serializer import (
    ProjectSpecificationSerializer,
)
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ProjectSpecificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project specifications to be viewed or edited.
    """

    queryset = ProjectSpecificationModel.objects.all().order_by(
        "project", "parent", "component", "function", "specification_order"
    )
    serializer_class = ProjectSpecificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project", "project_id", "parent"]

    def list(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id")
        category1 = request.query_params.get("category1")
        component_name = request.query_params.get("component_name")
        function_name = request.query_params.get("function_name")
        specification_type = request.query_params.get("specification_type")
        specification_name = request.query_params.get("specification_name")
        specification_version = request.query_params.get("specification_version")
        queryset = self.filter_queryset(self.get_queryset())
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if category1:
            queryset = queryset.filter(category1=category1)
        if component_name:
            queryset = queryset.filter(component__name=component_name.upper())
        if function_name:
            queryset = queryset.filter(function__name=function_name)
        if specification_type:
            queryset = queryset.filter(specification__type=specification_type)
        if specification_name:
            queryset = queryset.filter(
                specification__name__startswith=specification_name
            )
        if specification_version:
            queryset = queryset.filter(
                specification__revision__version=specification_version
            )
        items = queryset.order_by(
            "project", "parent", "component", "function", "specification_order"
        )
        page = self.paginate_queryset(items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(items, many=True)
            data = serializer.data

        for item in data:
            spec_id = item.get("specification")
            if isinstance(spec_id, dict):
                spec_id = spec_id.get("id")
            latest_revision = (
                SpecificationRevisionModel.objects.filter(specification_id=spec_id)
                .order_by("-change_date")
                .first()
            )
            item["specification_revision_change_summary"] = (
                latest_revision.change_summary if latest_revision else None
            )

        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in [
            "project",
            "component",
            "complexity",
            "function",
            "priority",
            "process",
            "specification",
            "parent",
        ]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()

            mutable_data = request.data.copy()

            for field in [
                "project",
                "component",
                "complexity",
                "function",
                "priority",
                "process",
                "specification",
                "parent",
            ]:
                field_id = f"{field}_id"
                if field_id in mutable_data:
                    mutable_data[field] = mutable_data.get(field_id)

            serializer = self.get_serializer(
                instance, data=mutable_data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            return f"Could not generate summary due to an error: {e}"
