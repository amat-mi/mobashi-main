# Generated by Django 4.2.5 on 2023-11-16 14:20

from django.db import migrations
from uuid import uuid4


def set_uuid_school(apps, schema_editor):
    MyModel = apps.get_model('momain', 'School')
    for obj in MyModel.objects.filter(uuid__isnull=True):
        obj.uuid = uuid4()
        obj.save(update_fields=['uuid'])

def set_uuid_campaign(apps, schema_editor):
    MyModel = apps.get_model('momain', 'Campaign')
    for obj in MyModel.objects.filter(uuid__isnull=True):
        obj.uuid = uuid4()
        obj.save(update_fields=['uuid'])


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0005_campaign_uuid_school_uuid"),
    ]

    operations = [
        migrations.RunPython(set_uuid_school),
        migrations.RunPython(set_uuid_campaign),
    ]