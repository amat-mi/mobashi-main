# -*- coding: utf-8 -*-

from . import RedoRoutingCommand

from django.contrib.gis.geos import LineString, MultiLineString
from momain.models import Trip, Stage, Trait, Link, Network
import requests


def redo_routing(mode, network_name='OSM', service='pgrouting', profile='car'):
    network = Network.objects.get(name=network_name)

    params = {
        "service": service,
        "profile": profile
    }

    for trip in Trip.objects.filter(stages__mode=mode):
        params["lng_from"] = trip.orig_geom.x
        params["lat_from"] = trip.orig_geom.y
        params["lng_to"] = trip.dest_geom.x
        params["lat_to"] = trip.dest_geom.y
        res = requests.get(
            "http://host.docker.internal:4001/rout/directions", params=params)
        data = res.json()
        path = data['result']['path']
        print(len(path))
        traits = Trait.objects.filter(stage__in=trip.stages.all())
        print(len(traits))
        traits.delete()
        stage = trip.stages.all()[0]
        for index in range(1, len(path) - 1):
            part = path[index]
            netid = part[0]
            try:
                link = Link.objects.get(network_id=network.id, netid=netid)
            except Link.DoesNotExist:
                prev = path[index - 1]
                geom = MultiLineString(LineString(
                    (prev[1], prev[2]), (part[1], part[2])), srid=4326)
                link = Link.objects.create(
                    network_id=network.id, netid=netid, geom=geom)
            trait = Trait.objects.create(stage=stage, ord=index, link=link)


class Command(RedoRoutingCommand):
    help = u'''
  '''

    def do_it(self, mode):
        if not mode:
            raise Exception(u'No "mode" specified')
        redo_routing(mode)
