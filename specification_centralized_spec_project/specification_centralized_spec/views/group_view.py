from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination
import django_filters

from specification_centralized_spec.serializers.group_serializer import GroupSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited by administration users.
    """
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["name"]