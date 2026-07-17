from django.urls import path, include
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.import_traceability_view import ImportTraceabilityViewSet

router = DefaultRouter()
router.register(r"import-traceability", ImportTraceabilityViewSet, basename="importtraceability")

urlpatterns = [
    path(
        "import-traceability/import_code_traceability_from_repos/",
        ImportTraceabilityViewSet.as_view({"post": "import_code_traceability_from_repos"}),
        name="import-code-traceability-from-repos",
    ),
    path(
        "import-traceability/import_code_traceability_from_prs/",
        ImportTraceabilityViewSet.as_view({"post": "import_code_traceability_from_prs"}),
        name="import-code-traceability-from-prs",
    ),
    path("", include(router.urls)),
]
