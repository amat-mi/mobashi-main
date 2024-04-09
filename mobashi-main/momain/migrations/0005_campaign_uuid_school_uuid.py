# Generated by Django 4.2.5 on 2023-11-16 14:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0004_alter_role_options_campaign"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="uuid",
            field=models.UUIDField(
                blank=True, default=uuid.uuid4, editable=False, null=True
            ),
        ),
        migrations.AddField(
            model_name="school",
            name="uuid",
            field=models.UUIDField(
                blank=True, default=uuid.uuid4, editable=False, null=True
            ),
        ),
    ]
