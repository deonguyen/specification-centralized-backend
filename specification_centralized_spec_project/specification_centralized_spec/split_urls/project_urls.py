from specification_centralized_spec.views.project_view import ProjectViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
urlpatterns = router.urls
