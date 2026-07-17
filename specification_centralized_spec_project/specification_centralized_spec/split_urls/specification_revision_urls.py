from django.urls import path
from specification_centralized_spec.views.specification_revision_view import SpecificationRevisionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"specification-revisions", SpecificationRevisionViewSet)

urlpatterns = [
    path(
        "specification-revisions/first/",
        SpecificationRevisionViewSet.as_view({"get": "first"}),
        name="specification-revision-first",
    ),
    path(
        "specification-revisions/distinct_version/",
        SpecificationRevisionViewSet.as_view({"get": "distinct_version"}),
        name="specification-revision-distinct-version",
    ),
] + router.urls
