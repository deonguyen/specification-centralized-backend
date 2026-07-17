from specification_centralized_core.models.complexity_model import ComplexityModel
from specification_centralized_spec.serializers.complexity_serializer import ComplexitySerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ComplexityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows complexities to be viewed or edited.
    """

    queryset = ComplexityModel.objects.all().order_by("name")
    serializer_class = ComplexitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "code", "name", "type"]
