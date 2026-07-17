from django.urls import path
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.vertex_ai_view import VertexAIView

router = DefaultRouter()
router.register(r"vertexai", VertexAIView, basename="vertexai")

# urlpatterns = [
#     path("vertexai/generatediagram/", VertexAIView.as_view({"post": "generatediagram"}), name="vertexai-generatediagram"),
#     path("vertexai/generatetestcases/", VertexAIView.as_view({"post": "generatetestcases"}), name="vertexai-generatetestcases"),
#     path("vertexai/diffsummary/", VertexAIView.as_view({"post": "diffsummary"}), name="vertexai-diffsummary"),
# ] + router.urls