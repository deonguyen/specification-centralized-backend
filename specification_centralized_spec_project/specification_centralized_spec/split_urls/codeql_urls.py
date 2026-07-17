from django.urls import path, include
from rest_framework.routers import DefaultRouter

from specification_centralized_spec.views.codeql_view import CodeQlViewSet


router = DefaultRouter()
router.register(r'codeql', CodeQlViewSet, basename='codeql')

urlpatterns = [
    path(
        'codeql/run_codeql_query/',
        CodeQlViewSet.as_view({'post': 'run_codeql_query'}),
        name='run-codeql-query',
    ),
    path(
        'codeql/execution_summary/',
        CodeQlViewSet.as_view({'get': 'execution_summary'}),
        name='execution-summary',
    ),
    path('', include(router.urls)),
]
