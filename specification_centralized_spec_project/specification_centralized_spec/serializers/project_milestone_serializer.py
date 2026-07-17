from specification_centralized_core.models.project_milestone_model import ProjectMilestoneModel
from rest_framework import serializers


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for the ProjectMilestone model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")

    class Meta:
        """Meta class for ProjectMilestoneSerializer."""

        model = ProjectMilestoneModel
        fields = "__all__"
