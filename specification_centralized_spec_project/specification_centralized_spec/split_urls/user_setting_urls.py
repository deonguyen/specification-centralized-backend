from rest_framework.routers import DefaultRouter
from specification_centralized_spec.views.user_setting_view import UserSettingViewSet

router = DefaultRouter()
router.register(r"usersettings", UserSettingViewSet, basename="usersetting")

urlpatterns = router.urls