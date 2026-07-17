from rest_framework import permissions, viewsets

from specification_centralized_core.models.test_execution_trace_model import TestExecutionTraceModel
from specification_centralized_spec.serializers.test_execution_trace_serializer import (
    TestExecutionTraceSerializer,
)


class TestExecutionTraceViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionTraceModel.objects.all().order_by("-id")
    serializer_class = TestExecutionTraceSerializer
    permission_classes = [permissions.IsAuthenticated]