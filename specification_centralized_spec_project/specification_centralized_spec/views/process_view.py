from specification_centralized_core.models.process_model import ProcessModel
from specification_centralized_spec.serializers.process_serializer import ProcessSerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class ProcessViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows processes to be viewed or edited.
    """

    queryset = ProcessModel.objects.all().order_by("name")
    serializer_class = ProcessSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "code", "name", "type"]
