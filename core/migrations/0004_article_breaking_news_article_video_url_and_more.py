# Generated by Django 5.0.7 on 2025-03-25 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_userprofile_is_editor'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='breaking_news',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='article',
            name='video_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='subscription_tier',
            field=models.CharField(choices=[('free', 'Free'), ('basic', 'Basic'), ('premium', 'Premium')], default='free', max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending Approval'), ('published', 'Published')], default='draft', max_length=20),
        ),
    ]
