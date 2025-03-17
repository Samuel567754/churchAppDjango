# Generated by Django 5.1.6 on 2025-03-13 07:48

import versatileimagefield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0010_alter_sermon_audio_file_alter_sermon_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='sermon',
            name='ppoi',
            field=versatileimagefield.fields.PPOIField(blank=True, default='0.5x0.5', editable=False, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='sermon',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
