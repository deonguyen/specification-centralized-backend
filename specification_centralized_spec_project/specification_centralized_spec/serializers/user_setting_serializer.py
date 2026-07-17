from rest_framework import serializers
from specification_centralized_core.models.user_setting_model import UserSettingModel


class UserSettingSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", allow_null=True)
    project_id = serializers.IntegerField(
        source="project.id", allow_null=True
    )
    project_name = serializers.ReadOnlyField(
        source="project.name", allow_null=True
    )

    class Meta:
        model = UserSettingModel
        fields = "__all__"
