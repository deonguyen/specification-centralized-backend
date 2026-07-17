from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from specification_centralized_core.models.notification_model import NotificationModel
from specification_centralized_spec.serializers.notification_serializer import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Notifications to be viewed or edited.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only query and interact with their own notifications
        return NotificationModel.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        notifications = self.get_queryset().filter(is_read=False)
        updated_count = notifications.update(is_read=True)
        return Response({"status": "success", "updated_count": updated_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="read")
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "success"}, status=status.HTTP_200_OK)