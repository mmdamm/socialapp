# Generated by Django 4.2.4 on 2023-10-21 15:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialapp', '0008_post_save'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='save',
            field=models.ManyToManyField(blank=True, related_name='save_post', to=settings.AUTH_USER_MODEL),
        ),
    ]