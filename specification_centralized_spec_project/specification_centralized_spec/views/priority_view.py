from specification_centralized_core.models.priority_model import PriorityModel
from specification_centralized_spec.serializers.priority_serializer import PrioritySerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class PriorityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows priorities to be viewed or edited.
    """

    queryset = PriorityModel.objects.all().order_by("name")
    serializer_class = PrioritySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "code", "name", "type"]
