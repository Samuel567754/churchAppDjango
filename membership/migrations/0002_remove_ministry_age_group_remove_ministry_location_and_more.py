# Generated by Django 5.1.6 on 2025-02-18 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ministry',
            name='age_group',
        ),
        migrations.RemoveField(
            model_name='ministry',
            name='location',
        ),
        migrations.RemoveField(
            model_name='ministry',
            name='meeting_schedule',
        ),
        migrations.RemoveField(
            model_name='ministry',
            name='meeting_time',
        ),
    ]
