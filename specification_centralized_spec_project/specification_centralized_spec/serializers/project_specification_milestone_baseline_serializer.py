from rest_framework import serializers
from specification_centralized_core.models.project_specification_milestone_baseline_model import (
    ProjectSpecificationMilestoneBaselineModel,
)


class ProjectSpecificationMilestoneBaselineSerializer(serializers.ModelSerializer):
    """Serializer for the Project Specification Milestone Baseline model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")
    project_milestone_id = serializers.ReadOnlyField(source="project_milestone.id")
    project_milestone_name = serializers.ReadOnlyField(source="project_milestone.name")
    project_specification_id = serializers.ReadOnlyField(
        source="project_specification.id"
    )
    specification_id = serializers.ReadOnlyField(source="specification.id")
    specification_name = serializers.ReadOnlyField(source="specification.name")
    specification_revision_id = serializers.ReadOnlyField(
        source="specification_revision.id"
    )
    specification_revision_version = serializers.ReadOnlyField(
        source="specification_revision.version"
    )
    specification_revision_content = serializers.ReadOnlyField(
        source="specification_revision.content"
    )
    specification_revision_name = serializers.ReadOnlyField(
        source="specification_revision.name"
    )


    user_id = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = ProjectSpecificationMilestoneBaselineModel
        fields = "__all__"
