from specification_centralized_core.models.project_specification_model import ProjectSpecificationModel
from rest_framework import serializers


class ProjectSpecificationSerializer(serializers.ModelSerializer):
    """Serializer for the ProjectSpecification model."""

    complexity_id = serializers.ReadOnlyField(source="complexity.id", allow_null=True)
    complexity_name = serializers.ReadOnlyField(source="complexity.name", allow_null=True)
    component_id = serializers.ReadOnlyField(source="component.id", allow_null=True)
    component_name = serializers.ReadOnlyField(source="component.name", allow_null=True)
    function_id = serializers.ReadOnlyField(source="function.id", allow_null=True)
    function_name = serializers.ReadOnlyField(source="function.name", allow_null=True)
    parent_id = serializers.ReadOnlyField(source="parent.id", allow_null=True)
    parent_name = serializers.ReadOnlyField(source="parent.specification.name", allow_null=True)
    priority_id = serializers.ReadOnlyField(source="priority.id", allow_null=True)
    priority_name = serializers.ReadOnlyField(source="priority.name", allow_null=True)
    process_id = serializers.ReadOnlyField(source="process.id", allow_null=True)
    process_name = serializers.ReadOnlyField(source="process.name", allow_null=True)
    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")
    specification_id = serializers.ReadOnlyField(source="specification.id", allow_null=True)
    specification_content = serializers.ReadOnlyField(source="specification.content", allow_null=True)
    specification_interface = serializers.ReadOnlyField(source="specification.interface", allow_null=True)
    specification_name = serializers.ReadOnlyField(source="specification.name", allow_null=True)
    specification_type = serializers.ReadOnlyField(source="specification.type", allow_null=True)
    specification_version = serializers.ReadOnlyField(source="specification.version", allow_null=True)
    specification_fullpath= serializers.ReadOnlyField(source="specification.local_file_fullpath", allow_null=True)
    specification_revision_change_summary = serializers.ReadOnlyField(source="specification_revision.change_summary", allow_null=True)
    
    class Meta:
        """Meta class for ProjectSpecificationSerializer."""

        model = ProjectSpecificationModel
        fields = "__all__"
