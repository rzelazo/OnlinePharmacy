# Generated by Django 3.2.5 on 2022-06-16 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total price of the order', max_digits=7),
        ),
    ]