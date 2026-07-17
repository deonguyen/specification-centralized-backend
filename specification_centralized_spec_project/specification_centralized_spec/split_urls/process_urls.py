from specification_centralized_spec.views.github_view import GitHubViewSet
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.process_view import ProcessViewSet

router = DefaultRouter()
router.register(r"process", ProcessViewSet)
urlpatterns = router.urls
