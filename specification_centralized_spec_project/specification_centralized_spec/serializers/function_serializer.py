from specification_centralized_core.models.function_model import FunctionModel
from rest_framework import serializers


class FunctionSerializer(serializers.ModelSerializer):
    """Serializer for the Function model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        """Meta class for FunctionSerializer."""

        model = FunctionModel
        fields = "__all__"
