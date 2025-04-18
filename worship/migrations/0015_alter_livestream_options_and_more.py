# Generated by Django 5.1.6 on 2025-04-18 18:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worship', '0014_remove_sermon_series_alter_sermon_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='livestream',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='description',
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='recorded_url',
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='scheduled_time',
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='stream_url',
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='thumbnail',
        ),
        migrations.RemoveField(
            model_name='livestream',
            name='viewers_count',
        ),
        migrations.AddField(
            model_name='livestream',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='When this entry was created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='livestream',
            name='video_url',
            field=models.URLField(blank=True, help_text='Public Facebook video post URL', null=True),
        ),
        migrations.AlterField(
            model_name='livestream',
            name='is_live',
            field=models.BooleanField(default=False, help_text='Whether this stream is currently live'),
        ),
    ]
