from django.urls import path
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.ai_view import AIView

router = DefaultRouter()
router.register(r"ai", AIView, basename="ai")

urlpatterns = [
    path("ai/generatediagram/", AIView.as_view({"post": "generatediagram"}), name="ai-generatediagram"),
    path("ai/generatetestcases/", AIView.as_view({"post": "generatetestcases"}), name="ai-generatetestcases"),
    path("ai/diffsummary/", AIView.as_view({"post": "diffsummary"}), name="ai-diffsummary"),
] + router.urls
