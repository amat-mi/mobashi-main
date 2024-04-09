# Generated by Django 4.2.5 on 2024-01-30 17:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0018_school_students"),
    ]

    operations = [
        migrations.AddField(
            model_name="trip",
            name="direction",
            field=models.IntegerField(
                blank=True,
                choices=[(-1, "Invalid"), (0, "Forth"), (1, "Back")],
                default=0,
            ),
        ),
    ]