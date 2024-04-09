# Generated by Django 4.2.5 on 2023-11-22 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0011_network_trip_stage_link"),
    ]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="network",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="triplinks",
                to="momain.network",
            ),
        ),
        migrations.AlterField(
            model_name="stage",
            name="network",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tripstages",
                to="momain.network",
            ),
        ),
    ]