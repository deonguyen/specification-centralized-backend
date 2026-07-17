from rest_framework import serializers
from specification_centralized_core.models.specification_test_suite_model import SpecificationTestSuiteModel


class SpecificationTestSuiteSerializer(serializers.ModelSerializer):
    """Serializer for the Specification Test Suite model."""

    project_id = serializers.ReadOnlyField(source="project.id")
    project_name = serializers.ReadOnlyField(source="project.name")
    specification_id = serializers.ReadOnlyField(source="specification.id")
    specification_name = serializers.ReadOnlyField(source="specification.name")
    specification_revision_id = serializers.ReadOnlyField(source="specification_revision.id")
    
    class Meta:
        model = SpecificationTestSuiteModel
        fields = "__all__"