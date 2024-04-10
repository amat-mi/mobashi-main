# Django Rest Framework view
from django.http import HttpResponseNotFound
from django.http.response import HttpResponseServerError, HttpResponseBadRequest, Http404
from django.core.exceptions import BadRequest
from django.utils import translation
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
import rules
from .models import Cascho, Campaign, School, Role, Trip, Stage, Network, \
    ViewDash, ViewDashheat, ViewDashtrip, ViewDashlink
from .serializers import StageSerializer, TripSerializer, CaschoSerializer, CampaignSerializer, SchoolSerializer, RoleSerializer, \
    ViewDashSerializer, ViewDashheatSerializer, ViewDashtripSerializer, ViewDashlinkSerializer
from .roleing import ensure_user, reset_password, remove_user
from rules.contrib.rest_framework import AutoPermissionViewSetMixin


class SpecialAutoPermissionViewSetMixin(AutoPermissionViewSetMixin):
    permission_type_map = {
        **AutoPermissionViewSetMixin.permission_type_map,
        "roles": "change"
    }


class SchoolRoleViewSet(SpecialAutoPermissionViewSetMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return School.by_user(School.objects.all(), 'pk', self.request.user)

    def update(self, request, *args, **kwargs):
        try:
            action = request.data.get('action', '')
            method = getattr(self, 'handle_' + action, None)
            if not method:
                raise ValueError('Invalid action')
            school = self.get_object()
            kind = self.request.data.get('kind', None)
            if not kind or kind not in ['principal', 'mobman']:
                raise ValueError('Invalid kind')
            is_momain_admin = rules.is_group_member('momain_admin')(request.user)        
            lang = self.request.data.get('lang', None)
            with translation.override(lang):
                return method(request, school, kind, is_momain_admin)
        except ValueError as exc:
            return Response({
                'error': 'BAD_REQUEST',
                'message': '{}'.format(str(exc)).encode("utf-8")
            }, status=HttpResponseBadRequest.status_code)
        except Exception as exc:
            return Response({
                'error': 'GENERIC_ERROR',
                'message': '{}'.format(str(exc)).encode("utf-8")
            }, status=HttpResponseServerError.status_code)

    def handle_ensure_user(self, request, school, kind, is_momain_admin):
        # NOOO!!! Always use School EMail!!!
        # email = self.request.data.get('email', None)
        email = None
        user, created = ensure_user(school, kind, request, is_momain_admin, email=email)
        return Response({
            'id': user.pk if user else None,
            'email': user.email if user else None,
            'kind': kind,
            'created': created
        })

    def handle_reset_password(self, request, school, kind, is_momain_admin):
        user_pk = self.request.data.get('user', None)
        if not user_pk:
            raise ValueError('Invalid user')
        # NOOO!!! Always use School EMail!!!
        # email = self.request.data.get('email', None)
        email = None
        user, reset = reset_password(
            school, kind, user_pk, request, is_momain_admin, email=email)
        return Response({
            'id': user.pk if user else None,
            'email': user.email if user else None,
            'reset': reset
        })

    def handle_remove_user(self, request, school, kind, is_momain_admin):
        user_pk = self.request.data.get('user', None)
        if not user_pk:
            raise ValueError('Invalid user')
        role_pk = self.request.data.get('role', None)
        if not role_pk:
            raise ValueError('Invalid role')
        user, removed = remove_user(school, kind, user_pk, role_pk, is_momain_admin)
        return Response({
            'id': user.pk if user else None,
            'removed': removed
        })


class SchoolViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return School.by_user(School.objects.all(), 'pk', self.request.user)


class RoleViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Role.by_user(Role.objects.all(), 'pk', self.request.user)


class CampaignViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Campaign.by_user(Campaign.objects.all(), 'schools', self.request.user)

    def get_serializer_context(self):
        res = super().get_serializer_context()
        schools = School.by_user(School.objects.all(), 'pk', self.request.user)
        res["schools"] = set(schools.values_list('pk', flat=True))
        return res


class CaschoViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CaschoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cascho.by_user(Cascho.objects.all(), 'school', self.request.user)


class TripViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = TripSerializer
    # create() MUST be accessible by anonymous
    # and other methods are already protected by get_queryset(), that filters by user
    permission_classes = []

    def get_queryset(self):
        res = Trip.objects.all()
        campaign_id = self.request.GET.get('campaign_id', None)
        if campaign_id:
            res = res.filter(campaign_id=campaign_id)
        campaign_uuid = self.request.GET.get('campaign_uuid', None)
        if campaign_uuid:
            try:
                campaign = Campaign.objects.get(uuid=campaign_uuid)
                res = res.filter(campaign_id=campaign.pk)
            except:
                raise NotFound()
        return Trip.by_user(res, 'school_id', self.request.user)


class StageViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = StageSerializer
    # create() MUST be accessible by anonymous
    # and other methods are already protected by get_queryset(), that filters by user
    permission_classes = []

    def get_queryset(self):
        return Stage.objects.all()


class DashViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ViewDashSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        res = Campaign.by_user(Campaign.objects.all(),
                               'schools', self.request.user)
        return res  # .select_related('dashes')

    def get_serializer_context(self):
        res = super().get_serializer_context()
        schools = School.by_user(School.objects.all(), 'pk', self.request.user)
        res["schools"] = set(schools.values_list('pk', flat=True))
        return res


class DashheatViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ViewDashheatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        res = ViewDashheat.objects.all()
        campaign_id = self.request.GET.get('campaign_id', None)
        if campaign_id:
            res = res.filter(campaign_id=campaign_id)
        campaign_uuid = self.request.GET.get('campaign_uuid', None)
        if campaign_uuid:
            try:
                campaign = Campaign.objects.get(uuid=campaign_uuid)
                res = res.filter(campaign_id=campaign.pk)
            except:
                raise NotFound()
        return ViewDashheat.by_user(res, 'school_id', self.request.user)


class DashtripViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ViewDashtripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        res = ViewDashtrip.objects.all()

        campaign_id = self.request.GET.get('campaign_id', None)
        if campaign_id:
            res = res.filter(campaign_id=campaign_id)
        campaign_uuid = self.request.GET.get('campaign_uuid', None)
        if campaign_uuid:
            try:
                campaign = Campaign.objects.get(uuid=campaign_uuid)
                res = res.filter(campaign_id=campaign.pk)
            except:
                raise NotFound()

        network_id = self.request.GET.get('network_id', None)
        if network_id:
            res = res.filter(network_id=network_id)
        network_uuid = self.request.GET.get('network_uuid', None)
        if network_uuid:
            try:
                network = Network.objects.get(uuid=network_uuid)
                res = res.filter(network_id=network.pk)
            except:
                raise NotFound()

        return ViewDashtrip.by_user(res, 'school_id', self.request.user)


class DashLinkViewSet(AutoPermissionViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ViewDashlinkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        res = ViewDashlink.objects.all()
        campaign_id = self.request.GET.get('campaign_id', None)
        if campaign_id:
            res = res.filter(campaign_id=campaign_id)
        campaign_uuid = self.request.GET.get('campaign_uuid', None)
        if campaign_uuid:
            try:
                campaign = Campaign.objects.get(uuid=campaign_uuid)
                res = res.filter(campaign_id=campaign.pk)
            except:
                raise NotFound()
        return res
