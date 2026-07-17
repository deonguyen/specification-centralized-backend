from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.test_execution_trace_view import TestExecutionTraceViewSet

router = DefaultRouter()
router.register(
    r"test-execution-traces", TestExecutionTraceViewSet, basename="test-execution-trace"
)

urlpatterns = router.urls
