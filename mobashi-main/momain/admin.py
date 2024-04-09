# Django Admin
from typing import Any
import json
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http.response import HttpResponse
from rules.contrib.admin import ObjectPermissionsModelAdmin
from .models import Campaign, Cascho, Network, School, Role
from .roleing import ensure_user
import rules
from contrib.oidjutils.utils import field_link


class BaseAdmin(ObjectPermissionsModelAdmin):
    save_on_top = True


class RoleInline(admin.TabularInline):
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Role.by_user(super().get_queryset(request), 'role_id', request.user)

    model = Role.schools.through
    extra = 1


class CampaignInline(admin.TabularInline):
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Campaign.by_user(super().get_queryset(request), 'school_id', request.user)

    model = Campaign.schools.through
    extra = 1


class SchoolAdmin(BaseAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return School.by_user(super().get_queryset(request), 'pk', request.user)

    inlines = [RoleInline, CampaignInline]
    list_display = ("name", "uuid", "code", "email", "students", "address")
    search_fields = ("name", "uuid", "code", "email", "address")

    actions = [
        'ensure_principal_user', 'ensure_mobman_user'
    ]

    def _ensure(self, request, queryset, method, kind):
        if not queryset:
            raise Exception(_("Select at least one instance"))
        if queryset.count() > 1:
            raise Exception(_("Select exactly one instance"))

        for school in queryset:
            try:
                obj, created = method(school, kind, request)
                res = json.dumps({
                    'id': obj.pk if obj else None,
                    'kind': kind,
                    'created': created
                }, sort_keys=True, indent=4, separators=(',', ': '))
                return HttpResponse(res, content_type="application/json")
            except Exception as exc:
                self.message_user(request, _(
                    u'Error: {}'.format(exc)), level=messages.ERROR)

    def ensure_principal_user(self, request, queryset):
        return self._ensure(request, queryset, ensure_user, 'principal')
    ensure_principal_user.short_description = _(u'Ensure Principal User')

    def ensure_mobman_user(self, request, queryset):
        return self._ensure(request, queryset, ensure_user, 'mobman')
    ensure_mobman_user.short_description = _(u'Ensure Mobman User')


admin.site.register(School, SchoolAdmin)


class RoleAdmin(BaseAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Role.by_user(super().get_queryset(request), 'pk', request.user)

    def user_links(self, obj):
        if not obj or not obj.pk:
            return None
        res = []
        for user in obj.users.all():
            res.append(field_link(
                user, target='_blank', textfield='__str__'))
        return mark_safe(u'<br />'.join(res))
    user_links.short_description = _('Users')

    def school_links(self, obj):
        if not obj or not obj.pk:
            return None
        res = []
        for school in obj.schools.all():
            res.append(field_link(
                school, target='_blank', textfield='__str__'))
        return mark_safe(u'<br />'.join(res))
    school_links.short_description = _('Schools')

    list_display = ("__str__", "kind", "user_links", "school_links")
    search_fields = ("users__username", "users__first_name", "users__last_name", "users__email",
                     "schools__name")
    list_filter = ("kind",)


admin.site.register(Role, RoleAdmin)


class CampaignAdmin(BaseAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Campaign.by_user(super().get_queryset(request), 'schools', request.user)

    def school_links(self, obj):
        if not obj or not obj.pk:
            return None
        res = []
        for school in obj.schools.all():
            res.append(field_link(
                school, target='_blank', textfield='__str__'))
        return mark_safe(u'<br />'.join(res))
    school_links.short_description = _('Schools')

    list_display = ("__str__", "uuid", "school_links",
                    "stamp_start", "stamp_end")
    search_fields = ("name", "uuid", "schools__name",)
    autocomplete_fields = ("schools",)


admin.site.register(Campaign, CampaignAdmin)


class CaschoAdmin(BaseAdmin):
    def qrcode(self, obj):
        try:
            qrcode = reverse('oidjutils:qrcode')
            return mark_safe(u'''
                <img src="{0}?path={1}&box_size=8" />
                <br />
                <a href="{1}" target="_blank">{2}</a>
            '''.format(qrcode, obj.url, obj))
        except Exception as exc:
            pass
    qrcode.short_description = _('Invito')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return Cascho.by_user(super().get_queryset(request), 'school', request.user)

    list_display = ('__str__',)
    search_fields = ('campaign__name', 'school__name',)
    ordering = ('campaign', 'school',)
    list_filter = ('campaign', 'school',)
    fields = ('__str__', 'qrcode',)
    readonly_fields = ('__str__', 'qrcode',)


admin.site.register(Cascho, CaschoAdmin)


class NetworkAdmin(BaseAdmin):
    list_display = ("__str__", "uuid",)
    search_fields = ("name", "uuid",)


admin.site.register(Network, NetworkAdmin)
