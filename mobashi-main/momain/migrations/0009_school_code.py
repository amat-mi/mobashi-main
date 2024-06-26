# Generated by Django 4.2.5 on 2023-11-21 10:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("momain", "0008_alter_campaign_uuid_alter_school_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="school",
            name="code",
            field=models.CharField(
                blank=True,
                help_text="Unique code of the school",
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Code",
            ),
        ),
    ]
