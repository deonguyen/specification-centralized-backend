from django.urls import include, path
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.specification_test_suite_view import SpecificationTestSuiteViewSet

router = DefaultRouter()
router.register(r"specification-test-suites", SpecificationTestSuiteViewSet, basename="specificationtestsuite")

urlpatterns = [
    path(
        "specification-test-suites/project_specification_test_suites/",
        SpecificationTestSuiteViewSet.as_view({"get": "project_specification_test_suites"}),
        name="project-specification-test-suites",
    ),
    path("", include(router.urls)),
]