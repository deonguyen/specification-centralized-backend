from specification_centralized_spec.views.github_view import GitHubViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"github", GitHubViewSet, basename="github")
urlpatterns = router.urls
