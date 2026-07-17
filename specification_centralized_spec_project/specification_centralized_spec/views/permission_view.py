from django.contrib.auth.models import Permission
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters

from specification_centralized_spec.serializers.permission_serializer import PermissionSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows permissions to be viewed by administration users.
    """
    queryset = Permission.objects.all().order_by("name")
    serializer_class = PermissionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["name", "content_type"]