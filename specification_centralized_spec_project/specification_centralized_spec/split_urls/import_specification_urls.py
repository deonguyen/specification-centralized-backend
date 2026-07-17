from django.urls import path, include
from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.import_specification_view import ImportSpecificationViewSet

router = DefaultRouter()
router.register(r"import-specifications", ImportSpecificationViewSet, basename="importspecification")

urlpatterns = [
    path(
        "import-specifications/import_specification_from_local_file/",
        ImportSpecificationViewSet.as_view({"post": "import_specification_from_local_file"}),
        name="import-specification-from-local-file",
    ),
    path(
        "import-specifications/import_specification_from_local_folder/",
        ImportSpecificationViewSet.as_view({"post": "import_specification_from_local_folder"}),
        name="import-specification-from-local-folder",
    ),
    path(
        "import-specifications/import_specification_from_google_drive/",
        ImportSpecificationViewSet.as_view({"post": "import_specification_from_google_drive"}),
        name="import-specification-from-google-drive",
    ),
    path(
        "import-specifications/import_specification_from_github/",
        ImportSpecificationViewSet.as_view({"post": "import_specification_from_github"}),
        name="import-specification-from-github",
    ),
    path(
        "import-specifications/import_specification_from_jama/",
        ImportSpecificationViewSet.as_view({"post": "import_specification_from_jama"}),
        name="import-specification-from-jama",
    ),
    path("", include(router.urls)),
]