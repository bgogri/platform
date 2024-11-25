# Generated by Django 4.2.2 on 2024-11-25 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engagement', '0004_rename_message_template_appnotificationtemplate_template_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appnotificationtemplate',
            name='event_type',
            field=models.CharField(choices=[('product.created', 'Product Created'), ('product.updated', 'Product Updated'), ('product.deleted', 'Product Deleted'), ('test.event', 'Test Event'), ('test.multiple_listeners', 'Test Multiple Listeners')], max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='emailnotificationtemplate',
            name='event_type',
            field=models.CharField(choices=[('product.created', 'Product Created'), ('product.updated', 'Product Updated'), ('product.deleted', 'Product Deleted'), ('test.event', 'Test Event'), ('test.multiple_listeners', 'Test Multiple Listeners')], max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='notifiableevent',
            name='event_type',
            field=models.CharField(choices=[('product.created', 'Product Created'), ('product.updated', 'Product Updated'), ('product.deleted', 'Product Deleted'), ('test.event', 'Test Event'), ('test.multiple_listeners', 'Test Multiple Listeners')], db_index=True, max_length=50),
        ),
    ]
