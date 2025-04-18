# Generated by Django 5.1.6 on 2025-04-05 08:43

import django.core.files.storage
import settings.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_alter_churchcalendar_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='churchcalendar',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='uploads/'),
        ),
        migrations.AddField(
            model_name='churchcalendar',
            name='image_url',
            field=models.URLField(blank=True, help_text='Optional URL for an external image', null=True),
        ),
    ]
