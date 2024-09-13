import json
import logging

from collections import defaultdict
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import MultipleObjectsReturned
from rest_framework.authentication import BaseAuthentication
from onadata.apps.logger.models import XForm
from guardian.shortcuts import assign_perm, remove_perm, get_objects_for_user


class QedAuthMiddleware(RemoteUserMiddleware):
    header = 'HTTP_X_AUTH_USERNAME'


# TODO(m1): inherit from https://github.com/encode/django-rest-framework/pull/5306
# TODO(m1): when the DRF version with that class lands
class QedRemoteUserAuth(BaseAuthentication):
    """
    REMOTE_USER authentication.

    To use this, set up your web server to perform authentication, which will
    set the REMOTE_USER environment variable. You will need to have
    'django.contrib.auth.backends.RemoteUserBackend in your
    AUTHENTICATION_BACKENDS setting
    """

    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = 'HTTP_X_AUTH_USERNAME'

    def authenticate(self, request):
        user = authenticate(remote_user=request.META.get(self.header))
        if user and user.is_active:
            return (user, None)


class QedRemoteUserAttributeMiddleware(object):
    username_header = 'HTTP_X_AUTH_USERNAME'
    email_header = 'HTTP_X_AUTH_EMAIL'
    roles_header = 'HTTP_X_AUTH_ROLES'

    def process_request(self, request):
        username = request.META.get(self.username_header, None)
        email = request.META.get(self.email_header, None)
        roles_json = request.META.get(self.roles_header, None)

        remote_user_ok = hasattr(request, 'user') and request.user.is_authenticated \
            and username and email

        if not remote_user_ok:
            return

        user = request.user

        QedRemoteUserAttributeMiddleware.process_user(user, email)
        QedRemoteUserAttributeMiddleware.process_roles(user, roles_json)

    @staticmethod
    def process_user(user, email):
        needs_saving = False

        if user.email != email:
            user.email = email
            needs_saving = True

        if needs_saving:
            user.save()

    @staticmethod
    def process_roles(user, roles_json):
        if not settings.USE_REMOTE_PERMS:
            return

        # Based on KC_PERMISSIONS_MAP from kpi
        PERMS_MAP = {
            'data_submit': 'report_xform',
            'data_view': 'view_xform',
            'data_edit': 'change_xform',
        }

        logger = logging.getLogger("console_logger")

        if roles_json is None:
            raise RuntimeError("Remote perms enabled, but header not found")

        # KT__${var.kt_form_id}__${var.kt_form_permission}
        roles = json.loads(roles_json)

        kt_roles = defaultdict(set)
        for r in roles:
            if not r.startswith('KT__'):
                continue

            _, form_id, perm = r.split('__')

            if perm not in PERMS_MAP.keys():
                continue

            kt_roles[form_id].add(PERMS_MAP[perm])

        existing_roles = defaultdict(set)
        for perm_name in PERMS_MAP.values():
            for form_id in get_objects_for_user(user, perm_name, XForm, with_superuser=False).values_list("id_string", flat=True):
                existing_roles[form_id].add(perm_name)

        for form_id in set(existing_roles.keys()) | set(kt_roles.keys()):
            try:
                xform = XForm.objects.get(id_string=form_id)
            except MultipleObjectsReturned:
                logger.warning("Multiple forms with id_string {}. This is not supported"
                               " for remote permissions management to avoid unexpected"
                               " sharing. Skipping.".format(form_id))
                continue

            current_perms = existing_roles[xform.id_string]
            target_perms = kt_roles[xform.id_string]

            to_remove = current_perms - target_perms
            to_add = target_perms - current_perms

            if len(to_remove) + len(to_add) > 0:
                logger.info("[{}] User {}, form {} ({}). Remove: {}, add: {}".format(
                    "perms_dry_run" if settings.REMOTE_PERMS_DRY_RUN else "perms",
                    user.username,
                    xform.title,
                    xform.id_string,
                    str(to_remove),
                    str(to_add)
                ))

            if settings.REMOTE_PERMS_DRY_RUN:
                continue

            map(lambda p: remove_perm(p, user, xform), to_remove)
            map(lambda p: assign_perm(p, user, xform), to_add)
