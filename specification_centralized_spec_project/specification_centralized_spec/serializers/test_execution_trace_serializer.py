from specification_centralized_core.models.test_execution_trace_model import TestExecutionTraceModel
from rest_framework import serializers


class TestExecutionTraceSerializer(serializers.ModelSerializer):
    """Serializer for the TestExecutionTrace model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")
    project_specification_id = serializers.ReadOnlyField(
        source="project_specification.id"
    )
    specification_id = serializers.ReadOnlyField(source="specification.id")
    specification_revision_id = serializers.ReadOnlyField(
        source="specification_revision.id"
    )

    class Meta:
        model = TestExecutionTraceModel
        fields = "__all__"