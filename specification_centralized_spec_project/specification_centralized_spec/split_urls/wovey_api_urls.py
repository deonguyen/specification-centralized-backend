from specification_centralized_spec.views.wovey_api_view import WoveyAPIView
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"vertexai", WoveyAPIView, basename="woveyapi")

# urlpatterns = [
#     path(
#         "woveyapi/diffsummary/",
#         WoveyAPIView.as_view({"post": "diffsummary"}),
#         name="woveyapi-diffsummary",
#     ),
# ] + router.urls
