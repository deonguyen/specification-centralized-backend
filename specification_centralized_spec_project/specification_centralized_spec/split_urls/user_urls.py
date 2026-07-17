from django.urls import include, path
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.user_view import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
