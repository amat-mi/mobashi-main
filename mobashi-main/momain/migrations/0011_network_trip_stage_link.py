# Generated by Django 4.2.5 on 2023-11-22 16:38

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import momain.models
import rules.contrib.models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0010_school_address_school_lat_school_lng"),
    ]

    operations = [
        migrations.CreateModel(
            name="Network",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        blank=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Distinctive name of the network",
                        max_length=100,
                        unique=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Network",
                "verbose_name_plural": "Networks",
            },
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "modes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=10),
                        blank=True,
                        default=momain.models.get_modes_default,
                        size=None,
                    ),
                ),
                ("trav_dist", models.FloatField(blank=True, null=True)),
                ("trav_time", models.FloatField(blank=True, null=True)),
                ("orig_stamp", models.DateTimeField(blank=True, null=True)),
                ("dest_stamp", models.DateTimeField(blank=True, null=True)),
                (
                    "orig_address",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                (
                    "dest_address",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                (
                    "orig_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "dest_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="trips",
                        to="momain.campaign",
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="trips",
                        to="momain.school",
                    ),
                ),
            ],
            options={
                "verbose_name": "Trip",
                "verbose_name_plural": "Trips",
            },
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Stage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ord", models.IntegerField(blank=True, default=0)),
                (
                    "mode",
                    models.CharField(blank=True, default="unknown", max_length=10),
                ),
                ("trav_dist", models.FloatField(blank=True, null=True)),
                ("trav_time", models.FloatField(blank=True, null=True)),
                ("orig_stamp", models.DateTimeField(blank=True, null=True)),
                ("dest_stamp", models.DateTimeField(blank=True, null=True)),
                ("netid", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "orig_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "dest_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "network",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tripstages",
                        to="momain.trip",
                    ),
                ),
                (
                    "trip",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stages",
                        to="momain.trip",
                    ),
                ),
            ],
            options={
                "verbose_name": "Stage",
                "verbose_name_plural": "Stages",
            },
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ord", models.IntegerField(blank=True, default=0)),
                ("trav_dist", models.FloatField(blank=True, null=True)),
                ("trav_time", models.FloatField(blank=True, null=True)),
                ("orig_stamp", models.DateTimeField(blank=True, null=True)),
                ("dest_stamp", models.DateTimeField(blank=True, null=True)),
                ("netid", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "orig_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "dest_geom",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.LineStringField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "network",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="triplinks",
                        to="momain.trip",
                    ),
                ),
                (
                    "stage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="links",
                        to="momain.stage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Link",
                "verbose_name_plural": "Links",
            },
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
    ]