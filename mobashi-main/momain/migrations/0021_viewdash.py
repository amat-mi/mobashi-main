# Generated by Django 4.2.5 on 2024-02-06 15:23

from django.db import migrations, models
import momain.models


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0020_alter_cascho_campaign_alter_cascho_school"),
    ]

    operations = [
        migrations.CreateModel(
            name="ViewDash",
            fields=[
                (
                    "campaign_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("school_id", models.BigIntegerField(blank=True, null=True)),
                ("flow", models.BigIntegerField(blank=True, null=True)),
                ("trav_dist", models.FloatField(blank=True, null=True)),
                ("trav_time", models.FloatField(blank=True, null=True)),
            ],
            options={
                "db_table": "momain_dash",
                "managed": False,
            },
            bases=(models.Model, momain.models.ByUserMixin),
        ),
    ]
