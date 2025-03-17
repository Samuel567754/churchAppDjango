# Generated by Django 5.1.6 on 2025-03-16 20:24

import settings.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_like_like_type_alter_like_liked_at_alter_like_post_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='featured_image',
            field=settings.fields.CompressedImageField(blank=True, help_text='Optional featured image for the post', null=True, upload_to='blog/'),
        ),
    ]
