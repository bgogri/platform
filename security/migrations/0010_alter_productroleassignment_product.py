# Generated by Django 4.2.2 on 2023-09-04 08:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("product_management", "0005_delete_challengelisting"),
        ("security", "0009_productroleassignment_product"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productroleassignment",
            name="product",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="product_management.product",
            ),
        ),
    ]
