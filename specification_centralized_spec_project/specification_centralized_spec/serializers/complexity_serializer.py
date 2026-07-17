from specification_centralized_core.models.complexity_model import ComplexityModel
from rest_framework import serializers


class ComplexitySerializer(serializers.ModelSerializer):
    """Serializer for the Complexity model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        model = ComplexityModel
        fields = "__all__"
