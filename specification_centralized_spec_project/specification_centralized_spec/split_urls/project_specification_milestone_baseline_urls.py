from django.urls import path, include
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.project_specification_milestone_baseline_view import (
    ProjectSpecificationMilestoneBaselineViewSet,
)

router = DefaultRouter()
router.register(
    r"project-specification-milestone-baselines",
    ProjectSpecificationMilestoneBaselineViewSet,
    basename="projectspecificationmilestonebaseline",
)

urlpatterns = [
    path(
        "project-specification-milestone-baselines/projectspecificationmilestonebaseline/",
        ProjectSpecificationMilestoneBaselineViewSet.as_view({"post": "project_specification_milestone_baseline"}),
        name="project-specification-milestone-baseline",
    ),
    path(
        "project-specification-milestone-baselines/getprojectspecificationmilestonebaselinebysql/",
        ProjectSpecificationMilestoneBaselineViewSet.as_view({"get": "get_project_specification_milestone_baseline_by_sql"}),
        name="get-baseline-data-by-sql",
    ),
    path(
        "project-specification-milestone-baselines/update_project_specification_milestone_baseline_version/",
        ProjectSpecificationMilestoneBaselineViewSet.as_view({"post": "update_project_specification_milestone_baseline_version"}),
        name="update-project-specification-milestone-baseline-version",
    ),
    path("", include(router.urls)),
]