from django.conf import settings
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from uuid import uuid4
import rules
from rules.contrib.models import RulesModel
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def has_role(kind: str, fld: str = None):
    @rules.predicate
    def inner(user: settings.AUTH_USER_MODEL, obj: 'School') -> bool:
        if obj is None:
            return rules.is_staff(user)
        if not user.is_authenticated:
            return False
        res = Role.objects.filter(users=user).filter(
            Q((f'schools__{fld}', obj)) if fld else Q((f'schools', obj)),
        )
        if kind != '__any__':
            res = res.filter(kind=kind)
        return res.exists()
        # return obj.users.contains(user)
    return inner


class ByUserMixin:
    by_user_field = None
    by_user_kind = None

    @classmethod
    def by_user(cls, queryset: QuerySet[Any], fld: str, user: settings.AUTH_USER_MODEL) -> QuerySet[Any]:
        if not user.is_authenticated:
            return queryset.model.objects.none()
        if rules.is_superuser(user) | rules.is_group_member('momain_admin')(user):
            return queryset
        if not cls.by_user_field or not cls.by_user_kind:
            return queryset
        roles = Role.objects.filter(users=user)
        if cls.by_user_kind != '__any__':
            roles = roles.filter(kind=cls.by_user_kind)
        pks = roles.values_list(cls.by_user_field, flat=True)
        return queryset.filter(Q((f'{fld}__in', pks))).distinct()


class School(RulesModel, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    uuid = models.UUIDField(default=uuid4, null=False,
                            blank=True, editable=False, unique=True)
    name = models.CharField(_('School'), max_length=100, unique=True,
                            help_text=_('Distinctive name of the school'))
    code = models.CharField(_('Code'), max_length=20, null=True, blank=True, unique=True,
                            help_text=_('Unique code of the school'))
    email = models.EmailField(max_length=254, null=True, blank=True)
    students = models.IntegerField(null=True, blank=True)
    address = models.CharField(_('Address'), max_length=300, null=True, blank=True,
                               help_text=_('Complete address of the school'))
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = _('School')
        verbose_name_plural = _('Schools')
        ordering = ['name']
        rules_permissions = {
            # only a proper admin can create a School (has_role() do NOT work here)
            # a Principal can modify a School (for example correct its name or address)
            # only a proper admin can delete a School
            # anyone with any Role can view a School
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin') | has_role('principal'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('__any__')
        }

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.uuid = uuid4()
        super(School, self).save(*args, **kwargs)


class Role(RulesModel, ByUserMixin):
    by_user_field = 'pk'
    by_user_kind = 'principal'

    KIND_CHOICES = [
        ('principal', _('Principal')),
        ('mobman', _('Mobility Manager')),
    ]

    kind = models.CharField(_('Kind'), max_length=50, choices=KIND_CHOICES,
                            help_text=_('Kind of role that this users assume in this schools'))
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='roles', blank=True,
        help_text=_('Users that can assume this role in this schools'))
    schools = models.ManyToManyField(
        School, related_name='roles', blank=True,
        help_text=_('Schools where this role is assumed by this users'))

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        rules_permissions = {
            # only a proper admin can create a Role (has_role() do NOT work here)
            # only a proper admin or a Principal can modify a Role
            # only a proper admin can delete a Role
            # a Principal can view a Role
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin') | has_role('principal', 'roles'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('principal', 'roles')
        }

    def __str__(self):
        return _("%(kind)s for %(schools)s") % {
            "kind": self.get_kind_display(),
            "schools": self.schools_abbrev()
        }

    def schools_abbrev(self):
        schools = self.schools.values_list("name", flat=True)
        return ', '.join([x[:15] for x in schools]) if schools else _('no school')


class Campaign(RulesModel, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    class Status(models.IntegerChoices):
        DISABLED = -100, _('Disabled')
        ACTIVE = 0, _('Active')
        BEFORE = 50, _('Before')
        AFTER = 100, _('After')

    uuid = models.UUIDField(default=uuid4, null=False,
                            blank=True, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True,
                            help_text='Distinctive name of the campaign')
    stamp_start = models.DateTimeField(
        help_text='Instant when the campaign becomes active')
    stamp_end = models.DateTimeField(
        help_text='Instant when the campaign stops to be active')
    schools = models.ManyToManyField(
        School, related_name='campaigns', blank=True,
        through='Cascho',
        help_text=_('Schools this campaign is about'))
    survey = models.JSONField(null=False, blank=True, default=dict)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-stamp_start', '-stamp_end']
        rules_permissions = {
            # only a proper admin can create a Campaign (has_role() do NOT work here)
            # only a proper admin can modify a Campaign
            # only a proper admin can delete a Campaign
            # anyone with any Role can view a Campaign
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('__any__', 'campaigns')
        }

    def __str__(self):
        return _("%(name)s") % {
            "name": self.name
        }

    @property
    def status(self):
        if self.stamp_start and self.stamp_end:
            now = timezone.now()
            return self.Status.BEFORE if now < self.stamp_start \
                else self.Status.AFTER if now >= self.stamp_end \
                else self.Status.ACTIVE
        return self.Status.DISABLED

    @property
    def status_label(self):
        return self.status.label

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.uuid = uuid4()
        super(Campaign, self).save(*args, **kwargs)

    def schools_abbrev(self):
        schools = self.schools.values_list("name", flat=True)
        return ', '.join([x[:15] for x in schools]) if schools else _('no school')


class Cascho(RulesModel, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    campaign = models.ForeignKey(
        Campaign, related_name='caschos', on_delete=models.CASCADE)
    school = models.ForeignKey(
        School, related_name='caschos', on_delete=models.CASCADE)

    class Meta:
        db_table = 'momain_campaign_schools'
        rules_permissions = {
            # only a proper admin can assign a School to a Campaign (has_role() do NOT work here)
            # only a proper admin can modify an assignment of a School to a Campaign
            # only a proper admin can delete an assignment of a School to a Campaign
            # a Principal can view an assignment of a School to a Campaign
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('principal', 'caschos')
        }

    def __str__(self):
        return _("%(campaign)s - %(school)s") % {
            "campaign": self.campaign,
            "school": self.school
        }

    @property
    def url(self):
        config = settings.SURV_CONFIG or {
            'CLIENT_URL': 'http://localhost:4102',
        }

        return _("%(client_url)s/surveyadd/%(campaign)s@%(school)s") % {
            "client_url": config['CLIENT_URL'],
            "campaign": self.campaign.uuid,
            "school": self.school.uuid
        }


class Network(RulesModel):
    uuid = models.UUIDField(default=uuid4, null=False,
                            blank=True, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True,
                            help_text='Distinctive name of the network')

    class Meta:
        verbose_name = _('Network')
        verbose_name_plural = _('Networks')
        rules_permissions = {
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | rules.is_authenticated
        }

    def __str__(self):
        return _("%(name)s") % {
            "name": self.name,
        }


class Link(RulesModel):
    network = models.ForeignKey(Network, related_name='links',
                                null=False, blank=False, on_delete=models.CASCADE)
    netid = models.CharField(max_length=100, null=False, blank=False)
    geom = models.MultiLineStringField(srid=4326, null=False, blank=False)

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')
        rules_permissions = {
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | rules.is_authenticated
        }

    def __str__(self):
        return _("%(network)s:%(netid)s") % {
            "network": self.network,
            "netid": self.netid,
        }


def get_modes_default():
    return list(['unknown'])


class Trip(RulesModel, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    class Direction(models.IntegerChoices):
        INVALID = -1, _('Invalid')
        FORTH = 0, _('Forth')
        BACK = 1, _('Back')

    extid = models.CharField(max_length=100, null=True, blank=True)
    school = models.ForeignKey(School, related_name='trips',
                               null=False, blank=False, on_delete=models.PROTECT)
    campaign = models.ForeignKey(Campaign, related_name='trips',
                                 null=False, blank=False, on_delete=models.PROTECT)
    direction = models.IntegerField(choices=Direction.choices,
                                    null=False, blank=True, default=Direction.FORTH)
    orig_stamp = models.DateTimeField(null=True, blank=True)
    dest_stamp = models.DateTimeField(null=True, blank=True)
    orig_address = models.CharField(max_length=300, null=True, blank=True)
    dest_address = models.CharField(max_length=300, null=True, blank=True)
    orig_geom = models.PointField(srid=4326, null=True, blank=True)
    dest_geom = models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        verbose_name = _('Trip')
        verbose_name_plural = _('Trips')
        rules_permissions = {
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('__any__', 'trips')
        }

    def __str__(self):
        return _("%(pk)s") % {
            "pk": self.pk,
        }


class Stage(RulesModel):
    trip = models.ForeignKey(Trip, related_name='stages',
                             null=False, blank=False, on_delete=models.CASCADE)
    ord = models.IntegerField(null=False, blank=True, default=0)
    mode = models.CharField(max_length=10, null=False, blank=False)
    orig_stamp = models.DateTimeField(null=True, blank=True)
    dest_stamp = models.DateTimeField(null=True, blank=True)
    orig_address = models.CharField(max_length=300, null=True, blank=True)
    dest_address = models.CharField(max_length=300, null=True, blank=True)
    orig_geom = models.PointField(srid=4326, null=True, blank=True)
    dest_geom = models.PointField(srid=4326, null=True, blank=True)

    class Meta:
        verbose_name = _('Stage')
        verbose_name_plural = _('Stages')
        rules_permissions = {
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('__any__', 'trips__stages')
        }

    def __str__(self):
        return _("%(pk)s") % {
            "pk": self.pk,
        }


class Trait(RulesModel):
    stage = models.ForeignKey(Stage, related_name='traits',
                              null=False, blank=False, on_delete=models.CASCADE)
    ord = models.IntegerField(null=False, blank=True, default=0)
    graphid = models.CharField(max_length=100, null=True, blank=True)
    submode = models.CharField(max_length=10, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    flow = models.FloatField(null=True, blank=True)
    trav_dist = models.FloatField(null=True, blank=True)
    trav_time = models.FloatField(null=True, blank=True)
    link = models.ForeignKey(Link, related_name='traits',
                             null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Trait')
        verbose_name_plural = _('Traits')
        rules_permissions = {
            "add": rules.is_group_member('momain_admin'),
            "change": rules.is_group_member('momain_admin'),
            "delete": rules.is_group_member('momain_admin'),
            "view": rules.is_group_member('momain_admin') | has_role('__any__', 'trips__stages__traits')
        }

    def __str__(self):
        return _("%(pk)s") % {
            "pk": self.pk,
        }


class ViewDash(models.Model, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    # not really a PK, but doesn't matter!!!
    # campaign_id = models.BigIntegerField(primary_key=True)
    campaign = models.ForeignKey(Campaign, related_name='dashes',
                                 null=True, blank=True, on_delete=models.DO_NOTHING)
    school_id = models.BigIntegerField(
        blank=True, null=False, primary_key=True)
    expected = ArrayField(models.BigIntegerField(blank=True, null=True))
    received = ArrayField(models.BigIntegerField(blank=True, null=True))
    uuid = models.UUIDField(default=uuid4, null=False,
                            blank=True, editable=False, unique=True)
    name = models.CharField(_('School'), max_length=100, unique=True,
                            help_text=_('Distinctive name of the school'))
    code = models.CharField(_('Code'), max_length=20, null=True, blank=True, unique=True,
                            help_text=_('Unique code of the school'))
    students = models.IntegerField(null=True, blank=True)
    address = models.CharField(_('Address'), max_length=300, null=True, blank=True,
                               help_text=_('Complete address of the school'))
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'momain_dash'


class ViewDashheat(models.Model, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    # not really a PK, but doesn't matter!!!
    extid = models.CharField(max_length=100, primary_key=True)
    campaign_id = models.BigIntegerField()
    school_id = models.BigIntegerField()
    modes = ArrayField(models.CharField(max_length=10))
    flow = models.FloatField(blank=True, null=True)
    trav_dist = models.FloatField(blank=True, null=True)
    trav_time = models.FloatField(blank=True, null=True)
    dir = models.IntegerField(blank=True, null=False)
    geom = models.GeometryField()

    class Meta:
        managed = False
        db_table = 'momain_dashheat'


class ViewDashtrip(models.Model, ByUserMixin):
    by_user_field = 'schools__pk'
    by_user_kind = '__any__'

    # not really a PK, but doesn't matter!!!
    campaign_id = models.BigIntegerField(
        blank=False, null=False, primary_key=True)
    school_id = models.BigIntegerField(blank=True, null=True)
    mode = models.CharField(max_length=10, blank=True, null=True)
    network_id = models.BigIntegerField(blank=True, null=True)
    netid = models.CharField(max_length=100, blank=True, null=True)
    flow = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'momain_dashtrip'


class ViewDashlink(models.Model):
    # not really a PK, but doesn't matter!!!
    campaign_id = models.BigIntegerField(
        blank=False, null=False, primary_key=True)
    data = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'momain_dashlink'
