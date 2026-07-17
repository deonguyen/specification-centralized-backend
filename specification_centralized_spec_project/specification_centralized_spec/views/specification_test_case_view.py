import os
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import django_filters
from django.db import connection

from specification_centralized_core.models.specification_test_case_model import SpecificationTestCaseModel
from specification_centralized_spec.serializers.specification_test_case_serializer import (
    SpecificationTestCaseSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = None
    page_size_query_param = "page_size"
    max_page_size = None


class SpecificationTestCaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows specification test cases to be viewed or edited.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = SpecificationTestCaseModel.objects.all()
    serializer_class = SpecificationTestCaseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["specification_test_suite_id", "status", "name"]

    def create(self, request, *args, **kwargs):
        mutable_data = request.data.copy()

        for field in ["project", "specification", "specification_revision"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        mutable_data = request.data.copy()

        for field in ["project", "specification", "specification_revision"]:
            field_id = f"{field}_id"
            if field_id in mutable_data:
                mutable_data[field] = mutable_data.get(field_id)

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
