# Generated by Django 3.2.5 on 2022-05-28 16:16

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(default='Poland', max_length=60)),
                ('city', models.CharField(max_length=60, validators=[core.models.validate_city_name])),
                ('postal_code', models.CharField(max_length=6, validators=[core.models.validate_postal_code])),
                ('street', models.CharField(max_length=60)),
                ('street_number', models.CharField(max_length=5)),
                ('local_number', models.CharField(max_length=5)),
            ],
            options={
                'verbose_name_plural': 'Addresses',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text="Customer's first name", max_length=30)),
                ('second_name', models.CharField(blank=True, help_text="Customer's second name", max_length=30, null=True)),
                ('last_name', models.CharField(help_text="Customer's last name", max_length=30)),
                ('date_of_birth', models.DateField(help_text="Customer's date of birth", validators=[core.models.validate_date])),
                ('phone_number', models.CharField(help_text="Customer's phone number", max_length=9, validators=[core.models.validate_phone_number])),
                ('gender', models.CharField(choices=[('m', 'Male'), ('f', 'Female')], help_text="Customer's gender", max_length=1)),
                ('user', models.ForeignKey(help_text='User account associated with this customer', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the product', max_length=60)),
                ('form', models.CharField(choices=[('TAB', 'tablets'), ('SYR', 'syrup'), ('GEL', 'gel')], help_text='The form of the product, eg. tablets, syrup etc.', max_length=3)),
                ('description', models.TextField(default='brak opisu')),
                ('net_weight', models.PositiveIntegerField(help_text='Net weight of the product (in grams)')),
                ('price', models.DecimalField(decimal_places=2, help_text='The regular price of the product', max_digits=6)),
                ('price_sale', models.DecimalField(blank=True, decimal_places=2, help_text='The sale price of the product', max_digits=6, null=True)),
                ('in_stock', models.PositiveBigIntegerField(help_text='Number of product pieces in stock')),
                ('image', models.ImageField(blank=True, null=True, upload_to='core/images/items')),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(help_text='The current status of the order', max_length=11, verbose_name=(('pre_payment', 'Awaiting payment'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('completed', 'Completed'), ('cancelled', 'Cancelled')))),
                ('customer', models.ForeignKey(help_text='Customer that have made this order', on_delete=django.db.models.deletion.CASCADE, to='core.customer')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.category')),
            ],
            options={
                'verbose_name_plural': 'Subcategories',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_pieces', models.PositiveIntegerField(help_text='Number of ordered item pieces')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.item')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(help_text='Items that the order comprises', through='core.OrderItem', to='core.Item'),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer',
            field=models.ForeignKey(help_text='The manufacturer of the product', on_delete=django.db.models.deletion.CASCADE, to='core.manufacturer'),
        ),
        migrations.AddField(
            model_name='item',
            name='subcategories',
            field=models.ManyToManyField(help_text='Subcategories to which the product belongs', to='core.SubCategory'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_pieces', models.PositiveIntegerField(help_text='Number of ordered item pieces')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.item')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.customer'),
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(help_text='Items that are in the cart', through='core.CartItem', to='core.Item'),
        ),
    ]
