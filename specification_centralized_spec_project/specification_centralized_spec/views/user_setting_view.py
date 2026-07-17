from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from specification_centralized_core.models.user_setting_model import UserSettingModel
from specification_centralized_spec.serializers.user_setting_serializer import UserSettingSerializer
import django_filters

from specification_centralized_spec.views.function_view import StandardResultsSetPagination


class UserSettingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user settings to be viewed or edited.
    """

    queryset = UserSettingModel.objects.all()
    serializer_class = UserSettingSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["user_id", "project_id"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        item = queryset.first()
        if item:
            serializer = self.get_serializer(item)
            data = serializer.data
        return Response(data)

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in [
            "user",
            "project",
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
            "user",
            "project",
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
