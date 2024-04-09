from django.conf import settings
from django.db import connections, transaction
from django.contrib.gis.geos import GEOSGeometry, LineString, MultiLineString

from .models import Stage, Trait, Network, Link


def get_route(mode: str, lng_from: float, lat_from: float, lng_to: float, lat_to: float, k=1):
    # HACK!!! Copied from ROUT server (it's pointless to invoke an API for such a short method)!!!

    dbalias = settings.ROUT_CONFIG.get('DBALIAS')
    if not dbalias:
        return []

    with connections[dbalias].cursor() as cursor:
        sql = f"select * from elab.routing_{mode}(%s, %s, %s, %s, %s)"
        cursor.execute(sql, [
            lat_from,
            lng_from,
            lat_to,
            lng_to,
            k or 1
        ])
        return cursor.fetchall()


def routing(mode: str, lng_from: float, lat_from: float, lng_to: float, lat_to: float, k=1):
    def to_dict(x):
        return {
            'ord': x[0],
            'submode': x[1],
            'agency': x[2],
            'route_id': x[3],
            'network': x[4],
            'netid': x[5],
            'graphid': x[6],
            'trav_dist': x[7],
            'trav_time': x[8],
            'flow': x[9],
            'geom': x[10]
        }

    route = get_route(mode, lng_from, lat_from, lng_to, lat_to, k)
    return list(to_dict(x) for x in route)


def foo_routing(stage: Stage):
    """
    Create a one Trait straight line routing for specified Stage.    
    """

    # remove when they'd become mandatory
    if not stage.orig_geom or not stage.dest_geom:
        return

    foonetwork = settings.ROUT_CONFIG.get('FOONETWORK', 'FOO')
    if not foonetwork:  # if setting unset
        return  # do not generate it

    orig_geom = stage.orig_geom.transform(3003, clone=True)
    dest_geom = stage.dest_geom.transform(3003, clone=True)
    trav_dist = dest_geom.distance(orig_geom)  # meter
    # seconds = seconds per hour * trav_dist / 30 Km/h
    trav_time = 3600 * trav_dist / 30000

    with transaction.atomic():
        stage.traits.all().delete()  # delete all existing Traits for this Stage

        trait = Trait(
            stage=stage,
            ord=0,
            flow=1.0,
            trav_dist=trav_dist,
            trav_time=trav_time
        )

        geom = MultiLineString(LineString(stage.orig_geom, stage.dest_geom))

        try:
            network = Network.objects.get(name=foonetwork)
            trait.link = Link.objects.get(
                network=network, netid=stage.pk)    # find fake Link for this Stage
            trait.link.geom = geom                  # update its geometry
            trait.link.save()
        except Network.DoesNotExist:
            raise  # should do something better here???
        except Link.DoesNotExist:
            trait.link = Link.objects.create(
                network=network, netid=stage.pk, geom=geom)  # create a fake Link for this Stage

        trait.save()


def actual_routing(stage: Stage):
    # remove when they'd become mandatory
    if not stage.orig_geom or not stage.dest_geom:
        return

    k = settings.ROUT_CONFIG.get('K', 1)
    if k < 1:
        k = 1
    if k > 4:
        k = 4

    route = routing(stage.mode,
                    stage.orig_geom.x, stage.orig_geom.y,
                    stage.dest_geom.x, stage.dest_geom.y,
                    k=k)
    if not route:
        return

    with transaction.atomic():
        stage.traits.all().delete()
        for part in route:
            infosep = ':' if part['agency'] and part['route_id'] else ''
            trait = Trait(
                stage=stage,
                ord=part['ord'],
                graphid=part['graphid'],
                submode=part['submode'],
                info=f"{part['agency']}{infosep}{part['route_id']}",
                flow=part['flow'] / 100,
                trav_dist=part['trav_dist'] / 100,
                trav_time=part['trav_time'] / 100,
            )

            geom = GEOSGeometry(part['geom'])
            if geom.simple:
                geom = MultiLineString(geom)            # ensure multi

            try:
                network = Network.objects.get(name=part['network'].upper())
                trait.link = Link.objects.get(
                    network=network, netid=part['netid'])
                # update its geometry (or should keep existing one???)
                trait.link.geom = geom
                trait.link.save()
            except Network.DoesNotExist:
                raise  # should do something better???
            except Link.DoesNotExist:
                trait.link = Link.objects.create(
                    network=network, netid=part['netid'], geom=geom)

            trait.save()
