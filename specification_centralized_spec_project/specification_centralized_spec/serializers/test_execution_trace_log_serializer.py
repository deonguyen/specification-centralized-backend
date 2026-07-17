from specification_centralized_core.models.test_execution_trace_log_model import (
    TestExecutionTraceLogModel,
)
from rest_framework import serializers


class TestExecutionTraceLogSerializer(serializers.ModelSerializer):
    """Serializer for the TestExecutionTraceLog model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")
    specification_test_case_id = serializers.ReadOnlyField(
        source="specification_test_case.id"
    )
    specification_test_suite_id = serializers.ReadOnlyField(
        source="specification_test_suite.id"
    )
    test_execution_trace_id = serializers.ReadOnlyField(
        source="test_execution_trace.id"
    )

    class Meta:
        model = TestExecutionTraceLogModel
        fields = "__all__"