# -*- coding: utf-8 -*-

from django.conf import settings
import httpx
from django.contrib.gis.geos import Point

from . import HarvestCommand
from momain.harvesting import harvest
from momain.tasks import async_harvest


class Command(HarvestCommand):
    help = u'''
  '''

    def do_it(self, doasync=False):
        if doasync:
            async_harvest()
        else:
            harvest()
