from rest_framework.routers import DefaultRouter

from specification_centralized_spec.views.component_view import ComponentViewSet

router = DefaultRouter()
router.register(r"components", ComponentViewSet)
urlpatterns = router.urls
