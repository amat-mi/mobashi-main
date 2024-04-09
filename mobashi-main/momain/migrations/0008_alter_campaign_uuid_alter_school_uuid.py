# Generated by Django 4.2.5 on 2023-11-16 15:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0007_alter_campaign_uuid_alter_school_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="uuid",
            field=models.UUIDField(
                blank=True, default=uuid.uuid4, editable=False, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="school",
            name="uuid",
            field=models.UUIDField(
                blank=True, default=uuid.uuid4, editable=False, unique=True
            ),
        ),
    ]