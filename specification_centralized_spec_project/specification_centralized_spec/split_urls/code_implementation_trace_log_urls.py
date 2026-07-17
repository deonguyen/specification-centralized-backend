from django.urls import path, include
from rest_framework.routers import DefaultRouter

from specification_centralized_spec.views.code_implementation_trace_log_view import CodeImplementationTraceLogViewSet


router = DefaultRouter()
router.register(r'code-implementation-trace-logs', CodeImplementationTraceLogViewSet, basename='code-implementation-trace-log')

urlpatterns = [
    path('', include(router.urls)),
]