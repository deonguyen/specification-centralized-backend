from specification_centralized_core.models.component_model import ComponentModel
from specification_centralized_spec.serializers.component_serializer import ComponentSerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ComponentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows components to be viewed or edited.
    """

    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "code", "name", "type"]
