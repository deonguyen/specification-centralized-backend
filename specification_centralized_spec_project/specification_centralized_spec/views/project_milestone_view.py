from specification_centralized_core.models.project_milestone_model import ProjectMilestoneModel
from specification_centralized_spec.serializers.project_milestone_serializer import (
    ProjectMilestoneSerializer,
)
from rest_framework import permissions, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project milestones to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = ProjectMilestoneModel.objects.all()
    serializer_class = ProjectMilestoneSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "project"]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in [
            "owner_user",
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
            "owner_user",
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
