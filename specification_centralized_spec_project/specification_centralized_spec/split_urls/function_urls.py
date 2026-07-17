from specification_centralized_spec.views.function_view import FunctionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"functions", FunctionViewSet)
urlpatterns = router.urls
