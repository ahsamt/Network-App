# Generated by Django 3.1.7 on 2021-08-25 12:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_auto_20210823_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likedBy',
            field=models.ManyToManyField(blank=True, related_name='likers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Like',
        ),
    ]
