# Generated by Django 4.2.2 on 2024-05-26 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product_management", "0040_remove_challenge_attachment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fileattachment",
            name="description",
        ),
        migrations.RemoveField(
            model_name="fileattachment",
            name="title",
        ),
    ]
