from specification_centralized_core.models.specification_model import SpecificationModel
from rest_framework import serializers


class SpecificationSerializer(serializers.ModelSerializer):
    """Serializer for the Specification model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    specification_id = serializers.ReadOnlyField(
        source="specification.id", allow_null=True
    )
    #specification_revision_change_summary = None

    class Meta:
        """Meta class for SpecificationSerializer."""

        model = SpecificationModel
        fields = "__all__"
