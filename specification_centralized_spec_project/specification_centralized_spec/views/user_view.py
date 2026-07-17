from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from specification_centralized_spec.serializers.user_serializer import UserSerializer
import django_filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["username", "email", "is_active"]
