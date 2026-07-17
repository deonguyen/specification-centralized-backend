from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.priority_view import PriorityViewSet

router = DefaultRouter()
router.register(r"priorities", PriorityViewSet, basename="priority")

urlpatterns = router.urls
