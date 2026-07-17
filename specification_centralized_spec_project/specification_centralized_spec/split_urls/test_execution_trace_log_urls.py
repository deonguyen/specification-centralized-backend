from rest_framework.routers import DefaultRouter

from specification_centralized_spec.views.test_execution_trace_log_view import (
    TestExecutionTraceLogViewSet,
)

router = DefaultRouter()
router.register(
    r"test-execution-trace-logs",
    TestExecutionTraceLogViewSet,
    basename="test-execution-trace-log",
)

urlpatterns = router.urls
