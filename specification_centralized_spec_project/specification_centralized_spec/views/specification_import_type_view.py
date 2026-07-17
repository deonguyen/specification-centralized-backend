from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters

from specification_centralized_core.models.specification_import_type_model import (
    SpecificationImportTypeModel,
)
from specification_centralized_spec.serializers.specification_import_type_serializer import (
    SpecificationImportTypeSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class SpecificationImportTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows specification import types to be viewed or edited.
    """

    queryset = SpecificationImportTypeModel.objects.all().order_by("name")
    serializer_class = SpecificationImportTypeSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["code", "name", "is_active"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)