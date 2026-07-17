from rest_framework import serializers
from specification_centralized_core.models.project_setting_model import ProjectSettingModel


class ProjectSettingSerializer(serializers.ModelSerializer):
    """Serializer for the ProjectSetting model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        """Meta class for ProjectSettingSerializer."""

        model = ProjectSettingModel
        fields = "__all__"
