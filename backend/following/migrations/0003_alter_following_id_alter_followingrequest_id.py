# Generated by Django 5.0.1 on 2024-02-23 23:24

import deadlybird.util
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('following', '0002_alter_following_id_alter_followingrequest_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='following',
            name='id',
            field=models.CharField(default=deadlybird.util.generate_next_id, max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='followingrequest',
            name='id',
            field=models.CharField(default=deadlybird.util.generate_next_id, max_length=255, primary_key=True, serialize=False),
        ),
    ]