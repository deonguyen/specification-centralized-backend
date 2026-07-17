from rest_framework import permissions, viewsets

from specification_centralized_core.models.test_execution_trace_log_model import TestExecutionTraceLogModel
from specification_centralized_spec.serializers.test_execution_trace_log_serializer import (
    TestExecutionTraceLogSerializer,
)


class TestExecutionTraceLogViewSet(viewsets.ModelViewSet):
    queryset = TestExecutionTraceLogModel.objects.all().order_by("-id")
    serializer_class = TestExecutionTraceLogSerializer
    permission_classes = [permissions.IsAuthenticated]