from django.urls import include, path
from specification_centralized_spec.views.project_milestone_view import ProjectMilestoneViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"project-milestones", ProjectMilestoneViewSet)

urlpatterns = [
    path("", include(router.urls)),
]