# Generated by Django 5.0.4 on 2024-05-01 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liveconfigs', '0002_historyevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='configrow',
            name='default_value',
            field=models.JSONField(blank=True, null=True),
        ),
    ]