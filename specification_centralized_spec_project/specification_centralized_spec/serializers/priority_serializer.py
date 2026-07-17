from rest_framework import serializers
from specification_centralized_core.models.priority_model import PriorityModel


class PrioritySerializer(serializers.ModelSerializer):
    """Serializer for the Priority model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        model = PriorityModel
        fields = "__all__"
