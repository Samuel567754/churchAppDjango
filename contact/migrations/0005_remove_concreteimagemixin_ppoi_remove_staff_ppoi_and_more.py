# Generated by Django 5.1.6 on 2025-03-16 20:24

import settings.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0004_concreteimagemixin_ppoi_staff_ppoi_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concreteimagemixin',
            name='ppoi',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='ppoi',
        ),
        migrations.AlterField(
            model_name='concreteimagemixin',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='image',
            field=settings.fields.CompressedImageField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
