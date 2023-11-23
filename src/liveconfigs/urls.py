from rest_framework.routers import DefaultRouter

from liveconfigs.views import ConfigRowViewSet

router = DefaultRouter()
router.register(prefix='configrow', viewset=ConfigRowViewSet, basename='configrow')
urlpatterns = router.urls
