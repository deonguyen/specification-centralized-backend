from django.urls import path, include
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.category_view import CategoryViewSet

router = DefaultRouter()
router.register(r"category", CategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
]