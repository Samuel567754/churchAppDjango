# Generated by Django 5.1.6 on 2025-03-20 13:52

import django.core.files.storage
import settings.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0005_remove_concreteimagemixin_ppoi_remove_staff_ppoi_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='attachment',
            field=settings.fields.SupabaseFileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to='newsletters/'),
        ),
    ]
