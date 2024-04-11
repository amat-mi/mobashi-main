from django.conf import settings
import httpx

from .exceptions import HandledError
from .models import School, Campaign, Cascho
from .serializers import SyncSchoolSerializer, SyncCampaignSerializer


def request(method, path, data):
    try:
        config = settings.SURV_CONFIG or {
            'SERVER_URL': 'http://host.docker.internal:4002',
        }
        secret = settings.SURV_SECRET or {}

        url = f"{config['SERVER_URL']}/surv/{path}/"
        key = secret['SERVER_KEY']
        headers = {'Authorization': f'Token {key}'}
        res = httpx.request(method, url, headers=headers, json=data)
        res.raise_for_status()

        # should do something with the result!!!
    except Exception as exc:
        raise HandledError from exc  # raise special error with Exception as __cause__


def sinc(instance: School | Campaign, url_suffix: str, serializer_class, created: bool):
    if created:
        method = 'POST'
        path = f"{url_suffix}"
    else:
        method = 'PATCH'
        path = f"{url_suffix}/{instance.uuid}"
    data = serializer_class(instance, many=False).data
    request(method, path, data)


def sinc_school(school: School, created: bool):
    sinc(school, 'schools', SyncSchoolSerializer, created)


def sinc_campaign(campaign: Campaign, created: bool):
    sinc(campaign, 'campaigns', SyncCampaignSerializer, created)


def sinc_cascho(campaign_uuid: str, school_uuid: str, add_school: bool):
    method = 'PATCH'
    if add_school:
        path = f"campaigns/{campaign_uuid}/add_school"
    else:
        path = f"campaigns/{campaign_uuid}/remove_school"
    data = {
        'school_uuid': school_uuid
    }
    request(method, path, data)
