from specification_centralized_core.models.component_model import ComponentModel
from rest_framework import serializers


class ComponentSerializer(serializers.ModelSerializer):
    """Serializer for the Component model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        """Meta class for ComponentSerializer."""

        model = ComponentModel
        fields = "__all__"
