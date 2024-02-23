# Generated by Django 5.0.1 on 2024-02-22 20:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("likes", "0002_alter_like_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="like",
            old_name="post",
            new_name="content_id",
        ),
        migrations.AddField(
            model_name="like",
            name="content_type",
            field=models.CharField(
                choices=[("post", "Post"), ("comment", "Comment")],
                default="post",
                max_length=50,
            ),
            preserve_default=False,
        ),
    ]