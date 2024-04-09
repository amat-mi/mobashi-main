from django.db.models.signals import post_save, post_delete

from .models import School, Campaign, Cascho, Stage
from .tasks import async_tosurv_school, async_tosurv_campaign, async_tosurv_cascho, async_actual_routing
from .routing import foo_routing


def post_save_School(sender, instance, created, *args, **kwargs):
    async_tosurv_school(instance.pk, created)


post_save.connect(post_save_School, sender=School)


def post_save_Campaign(sender, instance, created, *args, **kwargs):
    async_tosurv_campaign(instance.pk, created)


post_save.connect(post_save_Campaign, sender=Campaign)


def post_save_Cascho(sender, instance, created, *args, **kwargs):
    if created:                 #should always be True...
        async_tosurv_cascho(instance.campaign.uuid, instance.school.uuid, True)


post_save.connect(post_save_Cascho, sender=Cascho)


def post_delete_Cascho(sender, instance, *args, **kwargs):
    async_tosurv_cascho(instance.campaign.uuid, instance.school.uuid, False)


post_delete.connect(post_delete_Cascho, sender=Cascho)


def post_save_Stage(sender, instance, created, *args, **kwargs):
    # this is done synchronously
    foo_routing(instance)
    # this is done asynchronously
    async_actual_routing(instance.pk)


post_save.connect(post_save_Stage, sender=Stage)
