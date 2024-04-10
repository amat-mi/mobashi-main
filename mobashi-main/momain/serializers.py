# Django Rest Framework serializer
from django.urls import reverse
from rest_framework import serializers
from djoser.serializers import UserSerializer as DjoserUserSerializer
import rules
from .models import Campaign, School, Role, Cascho, Trip, Stage, \
    ViewDash, ViewDashheat, ViewDashtrip, ViewDashlink
from .roleing import is_username


##############################################
# Should go into django-oicom
class QRCodeSerializerMixin(object):

    def get_qrcode(self, obj):
        qrcode = reverse('oidjutils:qrcode')
        url = obj.url
        img = f"{qrcode}?path={url}&box_size=5"
        request = self.context.get("request")
        img = request.build_absolute_uri(img)
        return {
            'img': img,
            'url': url
        }


class PermsMixin(serializers.ModelSerializer):
    perms = serializers.SerializerMethodField()

    def get_perms(self, obj):
        user = self.context.get("request").user
        return {x: user.has_perm(obj.get_perm(x), obj)
                for x in ['add', 'change', 'delete', 'view']}


class SchoolsMixin:
    def get_schools(self, obj):
        return set(obj.schools.values_list('pk', flat=True)) & self.context.get("schools", [])


class UserSerializer(DjoserUserSerializer):
    is_admin = serializers.SerializerMethodField()
    perms = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('is_admin', 'perms')
        read_only_fields = DjoserUserSerializer.Meta.read_only_fields + \
            ('is_admin',)

    def get_is_admin(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        if rules.is_superuser(user) | rules.is_group_member('momain_admin')(user):
            return True
        return Role.objects.filter(users=user).filter(kind='principal').exists()

    def get_perms(self, obj):
        user = self.context.get("request").user
        res = {}

        def _add_perms(model, name):
            perms = model._meta.rules_permissions
            for perm_type, predicate in perms.items():
                res.setdefault(name, {})[perm_type] = predicate(user)

        _add_perms(Campaign, 'campaign')
        _add_perms(School, 'school')
        _add_perms(Role, 'role')
        _add_perms(Cascho, 'cascho')
        return res


class RoleSerializer(PermsMixin, serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class InnerUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'date_joined', 'last_login']


class SchoolSerializer(PermsMixin, serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = '__all__'

    def get_users(self, obj):
        user = self.context.get("request").user
        is_momain_admin = rules.is_group_member('momain_admin')(user)
        res = []
        for role in obj.roles.order_by('-kind').all():
            for user in role.users.all():  
                # only proper admin can see all Users of a School, 
                # other Users only see Users created by "ensure_user()" method
                if not is_momain_admin and not is_username(obj, role.kind, user.username):
                    continue
                data = InnerUserSerializer(user).data
                data['role'] = role.pk
                data['kind'] = role.kind
                data['perms'] = self.get_perms(role)
                res.append(data)
        return res


class SyncSchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ['uuid', 'name', 'code', 'address', 'lat', 'lng']


class CampaignSerializer(PermsMixin, SchoolsMixin, serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    schools = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'


class SyncCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = Campaign
        fields = ['uuid', 'name', 'stamp_start', 'stamp_end']


class CaschoSerializer(QRCodeSerializerMixin, PermsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    qrcode = serializers.SerializerMethodField()
    campaign_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Cascho
        fields = '__all__'

    def get_name(self, obj):
        return str(obj)

    def get_campaign_name(self, obj):
        return str(obj.campaign)

    def get_school_name(self, obj):
        return str(obj.school)


class TripSerializer(PermsMixin, serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = '__all__'


class StageSerializer(PermsMixin, serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'


class InnerViewDashSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='school_id')

    class Meta:
        model = ViewDash
        fields = ['id', 'expected', 'received', 'uuid', 'name', 'code',
                  'students', 'address', 'lat', 'lng']


class ViewDashSerializer(SchoolsMixin, serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    schools = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'

    def get_schools(self, obj):
        schools = super().get_schools(obj)
        dashes = obj.dashes.filter(school_id__in=schools)
        return InnerViewDashSerializer(dashes, many=True).data


class ViewDashheatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewDashheat
        fields = '__all__'


class ViewDashtripSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewDashtrip
        fields = '__all__'


class ViewDashlinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewDashlink
        fields = '__all__'
