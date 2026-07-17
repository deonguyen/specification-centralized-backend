from rest_framework import serializers
from specification_centralized_core.models.notification_model import NotificationModel

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = ["id", "user", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "user", "created_at"]