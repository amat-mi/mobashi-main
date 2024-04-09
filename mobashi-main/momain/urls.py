# Django Rest Framework url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StageViewSet, TripViewSet, CaschoViewSet, CampaignViewSet, \
    DashViewSet, DashLinkViewSet, DashheatViewSet, DashtripViewSet, \
    SchoolRoleViewSet, SchoolViewSet, RoleViewSet

router = DefaultRouter()
router.register(r'schoolroles', SchoolRoleViewSet, basename="schoolrole")
router.register(r'schools', SchoolViewSet, basename="school")
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'caschos', CaschoViewSet, basename='cascho')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'stages', StageViewSet, basename='stage')
router.register(r'dashes', DashViewSet, basename='dash')
router.register(r'dashheats', DashheatViewSet, basename='dashheat')
router.register(r'dashtrips', DashtripViewSet, basename='dashtrip')
router.register(r'dashlinks', DashLinkViewSet, basename='dashlink')

urlpatterns = [
    path('', include(router.urls)),
]
