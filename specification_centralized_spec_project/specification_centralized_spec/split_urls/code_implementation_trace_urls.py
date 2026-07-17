from django.urls import path, include
from rest_framework.routers import DefaultRouter

from specification_centralized_spec.views.code_implementation_trace_view import CodeImplementationTraceViewSet


router = DefaultRouter()
router.register(r'code-implementation-traces', CodeImplementationTraceViewSet, basename='code-implementation-trace')

urlpatterns = [
    path(
        'code-implementation-traces/get_code_dependency_traces/',
        CodeImplementationTraceViewSet.as_view({'get': 'get_code_dependency_traces'}),
        name='get-code-dependency-traces',
    ),
    path('', include(router.urls)),
]