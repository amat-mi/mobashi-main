# Generated by Django 4.2.5 on 2024-02-23 15:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0025_auto_20240223_1650"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stage",
            name="info",
        ),
    ]