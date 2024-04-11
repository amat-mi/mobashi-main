from django.conf import settings
import httpx
from django.contrib.gis.geos import Point

from .exceptions import HandledError
from .models import Trip, Campaign, School, Stage


def harvest():
    try:
        config = settings.SURV_CONFIG or {
            'SERVER_URL': 'http://host.docker.internal:4002',
        }
        secret = settings.SURV_SECRET or {}

        url = f"{config['SERVER_URL']}/surv/harvests/"
        key = secret['SERVER_KEY']
        headers = {'Authorization': f'Token {key}'}
        res = httpx.get(url, headers=headers)
        res.raise_for_status()
        jtrips = res.json()
        for jtrip in jtrips:
            stages = []
            ord = 0
            for jstage in jtrip.get('stages', []):
                stages.append(
                    Stage(
                        ord=ord,
                        mode=jstage['mode'],
                        orig_stamp=jstage['orig_stamp'],
                        dest_stamp=jstage['dest_stamp'],
                        orig_address=jstage['orig']['address'],
                        dest_address=jstage['dest']['address'],
                        orig_geom=Point(
                            jstage['orig']['lng'],
                            jstage['orig']['lat'],
                            srid=4326),
                        dest_geom=Point(
                            jstage['dest']['lng'],
                            jstage['dest']['lat'],
                            srid=4326)
                    )
                )
                ord += 1

            if not stages:
                continue                     # should raise or something???

            extid = jtrip['id']
            try:
                # remove existing Trip with same "extid", if any
                Trip.objects.filter(extid=extid).delete()
            except:
                pass

            trip = Trip.objects.create(
                extid=extid,
                campaign=Campaign.objects.get(uuid=jtrip['campaign']),
                school=School.objects.get(uuid=jtrip['school']),
                direction=Trip.Direction.FORTH if jtrip['kind'] in (0, 'forth')
                else Trip.Direction.BACK if jtrip['kind'] in (1, 'back')
                else Trip.Direction.INVALID,
                orig_geom=stages[0].orig_geom,
                dest_geom=stages[-1].dest_geom
            )

            for stage in stages:
                stage.trip = trip
                stage.save()

            url = f"{config['SERVER_URL']}/surv/harvests/{trip.extid}/"
            res = httpx.patch(url, headers=headers, json={"status": 100})
            # should do something with the result!!!
    except Exception as exc:
        raise HandledError from exc  # raise special error with Exception as __cause__
