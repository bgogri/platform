# Generated by Django 4.2.2 on 2024-11-06 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0057_alter_initiative_product'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['slug'], name='product_man_slug_74fe12_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['organisation'], name='product_man_organis_d3e00b_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['person'], name='product_man_person__714b9f_idx'),
        ),
    ]
