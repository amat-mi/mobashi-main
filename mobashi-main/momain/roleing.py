from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from djoser.compat import get_user_email as djoser_get_user_email
from djoser.conf import settings as djoser_settings
from .models import School, Role


User = get_user_model()


def build_username(school: School, kind: str):
    if not school.code:
        raise ValueError(_('Empty "code" field in School'))
    return f'{school.code}[{kind}]'


def is_username(school: School, kind: str, username: str):
    try:
        return username == build_username(school, kind)
    except ValueError:
        return False


def build_password():
    return get_random_string(10)


def ensure_user(school: School, kind: str, request, is_momain_admin: bool, email: str = None):
    if not email:
        email = school.email
    if not email:
        raise ValueError(
            _('No "email" specified and empty "email" field in School'))

    username = build_username(school, kind)
    with transaction.atomic():
        try:
            res = User.objects.get(username=username)
            created = False
        except User.DoesNotExist:
            res = User.objects.create_user(
                username=username,
                password=build_password(),
                email=email
            )
            created = True

        if not Role.objects.filter(schools=school, kind=kind, users=res).exists():
            role = Role.objects.create(
                kind=kind
            )
            role.schools.add(school)
            role.users.add(res)
            created = True

        # If User created, or "email" changed, must reset its password too
        if created or res.email != email:
            reset_password(school, kind, res.pk, request,
                           is_momain_admin, email=email)

        return res, created


def reset_password(school: School, kind: str, user_pk: int, request, is_momain_admin: bool, email: str = None):
    if not email:
        email = school.email

    with transaction.atomic():
        if not school.roles.filter(users=user_pk).exists():
            raise ValueError(_('Specified User has no Role in School'))

        user = get_object_or_404(User, pk=user_pk)

        # If the "username" of User to reset password for didn't come from "build_username()" method,
        # only a proper Admin can reset it's password
        # If instead the "username" did come from "build_username()" method, set the User "email" field,
        # but only if there actually is one
        if user.username != build_username(school, kind):
            if not is_momain_admin:
                raise ValueError(_('Specified User is not specific to School'))
        elif email:
            user.email = email
            user.save()

        # User must have the "email" field set somehow, or it's an error
        if not user.email:
            raise ValueError(
                _('No "email" specified and empty "email" field in School and empty "email" field in User'))

        # from Djoser.views.reset_password()
        context = {"user": user}
        to = [djoser_get_user_email(user)]
        djoser_settings.EMAIL.password_reset(request, context).send(to)

        return user, True


def remove_user(school: School, kind: str, user_pk: int, role_pk: int, is_momain_admin: bool):
    role = get_object_or_404(Role, pk=role_pk)

    with transaction.atomic():
        if not role.users.filter(pk=user_pk).exists():
            raise ValueError(
                _('Specified User has not specified Role in School'))

        user = get_object_or_404(User, pk=user_pk)

        # If the "username" of User to reset password for didn't come from "build_username()" method,
        # only a proper Admin can remove it
        if user.username != build_username(school, kind):
            if not is_momain_admin:
                raise ValueError(_('Specified User is not specific to School'))

        role.users.remove(user)

        return user, True
