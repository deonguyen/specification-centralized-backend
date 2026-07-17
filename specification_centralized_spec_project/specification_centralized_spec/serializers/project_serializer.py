from specification_centralized_core.models.project_model import ProjectModel
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for the Project model."""

    owner_user_id = serializers.ReadOnlyField(source="owner_user.id")
    owner_email = serializers.ReadOnlyField(source="owner_user.email")
    owner_firstname = serializers.ReadOnlyField(source="owner_user.first_name")
    owner_lastname = serializers.ReadOnlyField(source="owner_user.last_name")
    owner_username = serializers.ReadOnlyField(source="owner_user.username")

    class Meta:
        """Meta class for ProjectSerializer."""

        model = ProjectModel
        fields = "__all__"
