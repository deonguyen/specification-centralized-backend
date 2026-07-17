from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.specification_import_type_view import SpecificationImportTypeViewSet

router = DefaultRouter()
router.register(r"specification-import-types", SpecificationImportTypeViewSet, basename="specificationimporttype")

urlpatterns = router.urls