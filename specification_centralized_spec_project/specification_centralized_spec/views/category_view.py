from specification_centralized_core.models import CategoryModel
from specification_centralized_spec.serializers.category_serializer import CategorySerializer
from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from specification_centralized_spec.views.project_view import StandardResultsSetPagination
import django_filters


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """

    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["code", "name", "project"]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in ["project"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        mutable_data = request.data.copy()

        for field in ["project"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)