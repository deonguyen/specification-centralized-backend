from rest_framework import serializers
from specification_centralized_core.models.specification_import_type_model import (
    SpecificationImportTypeModel,
)


class SpecificationImportTypeSerializer(serializers.ModelSerializer):
    """Serializer for the SpecificationImportType model."""

    created_by_id = serializers.ReadOnlyField(source="created_by.id")
    created_by_username = serializers.ReadOnlyField(source="created_by.username")
    updated_by_id = serializers.ReadOnlyField(source="updated_by.id")
    updated_by_username = serializers.ReadOnlyField(source="updated_by.username")

    class Meta:
        model = SpecificationImportTypeModel
        fields = "__all__"
        read_only_fields = ["created_at", "created_by", "updated_at", "updated_by"]