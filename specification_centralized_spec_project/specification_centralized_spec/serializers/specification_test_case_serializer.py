from rest_framework import serializers
from specification_centralized_core.models.specification_test_case_model import SpecificationTestCaseModel


class SpecificationTestCaseSerializer(serializers.ModelSerializer):
    """Serializer for the Specification Test Case model."""

    # Read-only fields to provide context from the parent test suite
    project_id = serializers.ReadOnlyField(source="test_suite.project.id")
    project_name = serializers.ReadOnlyField(source="test_suite.project.name")
    specification_id = serializers.ReadOnlyField(source="test_suite.specification.id")
    specification_name = serializers.ReadOnlyField(source="test_suite.specification.name")
    specification_revision_id = serializers.ReadOnlyField(source="specification_revision.id")
    specification_test_suite_id = serializers.ReadOnlyField(source="specification_test_suite.id")
    specification_test_suite_name   = serializers.ReadOnlyField(source="specification_test_suite.name")

    class Meta:
        model = SpecificationTestCaseModel
        fields = "__all__"
