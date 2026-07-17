from specification_centralized_core.models.function_model import FunctionModel
from specification_centralized_spec.serializers.function_serializer import FunctionSerializer
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class FunctionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows functions to be viewed or edited.
    """

    queryset = FunctionModel.objects.all()
    serializer_class = FunctionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["project_id", "code", "name", "type"]
