from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.local_file_view import LocalFileViewSet

router = DefaultRouter()
router.register(r"localfiles", LocalFileViewSet, basename="localfile")

urlpatterns = router.urls