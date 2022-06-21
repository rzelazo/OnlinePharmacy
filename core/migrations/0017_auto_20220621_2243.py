# Generated by Django 3.2.5 on 2022-06-21 20:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_address_local_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('dhl', 'Kurier DHL'), ('inpost', 'Paczkomaty inPost'), ('self-pickup', 'Odbiór osobisty')], default='dhl', help_text='Delivery method chosen by the customer', max_length=11),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('dp', 'Przelew'), ('card', 'Karta płatnicza'), ('blik', 'BLIK')], default='dp', help_text='Payment method chosen by the customer', max_length=4),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(default=1, help_text='Customer that have made this order', on_delete=django.db.models.deletion.CASCADE, to='core.customer'),
            preserve_default=False,
        ),
    ]
