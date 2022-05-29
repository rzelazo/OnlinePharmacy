import re

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.validators import ValidationError
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return f"{self.category} > {self.name}"


class Manufacturer(models.Model):
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.name


class Item(models.Model):
    TABLETS = 'TAB'
    SYRUP = 'SYR'
    GEL = 'GEL'
    FORM_CHOICES = (
        (TABLETS, 'tablets'),
        (SYRUP, 'syrup'),
        (GEL, 'gel')
    )

    name = models.CharField(max_length=60, help_text="Name of the product")
    subcategories = models.ManyToManyField(to='SubCategory', help_text="Subcategories to which the product belongs")
    form = models.CharField(max_length=3, choices=FORM_CHOICES,
                            help_text="The form of the product, eg. tablets, syrup etc.")

    description = models.TextField(default="brak opisu")

    net_weight = models.PositiveIntegerField(help_text="Net weight of the product (in grams)")
    price = models.DecimalField(max_digits=6, decimal_places=2, help_text="The regular price of the product")
    # if 'price_sale' not null it overrides the regular 'price'
    price_sale = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                     help_text="The sale price of the product")

    manufacturer = models.ForeignKey(to='Manufacturer', on_delete=models.CASCADE,
                                     help_text="The manufacturer of the product")
    in_stock = models.PositiveBigIntegerField(help_text="Number of product pieces in stock")
    image = models.ImageField(upload_to='core/images/items', null=True, blank=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.OneToOneField(to='Customer', on_delete=models.CASCADE)
    items = models.ManyToManyField(to='Item', through='CartItem', help_text="Items that are in the cart")

    def __str__(self):
        return f"{self.customer}'s cart"


class CartItem(models.Model):
    """
    Intermediary table between Cart and Item tables.
    """
    cart = models.ForeignKey(to='Cart', on_delete=models.CASCADE)
    item = models.ForeignKey(to='Item', on_delete=models.CASCADE)
    n_pieces = models.PositiveIntegerField(help_text="Number of ordered item pieces")

    def __str__(self):
        return f"{self.n_pieces} piece{'s' if self.n_pieces > 1 else ''} of {self.item}"

    def clean(self, *args, **kwargs):
        if self.n_pieces > self.item.in_stock:
            raise ValidationError({'n_pieces': "Not enough pieces in stock!"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


DATE_VALIDATION_ERRORS = {
    'future_date_error': ValidationError(message="Date cannot be from the future!", code='future_date_error'),
    'too_young_error': ValidationError(message="User must be at least 13 years old!", code='too_young_error')
}


def validate_date(date):
    now = timezone.now().date()
    error_keys = []
    if date > now:
        error_keys.append('future_date_error')
    if date > now - timedelta(days=13 * 365):
        error_keys.append('too_young_error')

    if len(error_keys) > 0:
        raise ValidationError([DATE_VALIDATION_ERRORS[error_key] for error_key in error_keys])


PHONE_NUMBER_VALIDATION_ERRORS = {
    'len_error': ValidationError('Phone number must be exactly 9 digits', code='len_error'),
    'not_digits_error': ValidationError('Phone number must contain only digits!', code='not_digits_error')
}


def validate_phone_number(phone_number):
    error_keys = []
    if len(phone_number) < 9:
        error_keys.append('len_error')
    if not phone_number.isdigit():
        error_keys.append('not_digits_error')

    if len(error_keys) > 0:
        raise ValidationError([PHONE_NUMBER_VALIDATION_ERRORS[error_key] for error_key in error_keys])


class Customer(models.Model):
    MALE = 'm'
    FEMALE = 'f'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    first_name = models.CharField(max_length=30, help_text="Customer's first name")
    second_name = models.CharField(max_length=30, null=True, blank=True, help_text="Customer's second name")
    last_name = models.CharField(max_length=30, help_text="Customer's last name")
    date_of_birth = models.DateField(validators=[validate_date], help_text="Customer's date of birth")
    phone_number = models.CharField(max_length=9, validators=[validate_phone_number],
                                    help_text="Customer's phone number")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, help_text="Customer's gender")
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             help_text="User account associated with this customer")

    def __str__(self):
        if self.second_name is not None:
            return f"{self.first_name} {self.second_name} {self.last_name}"
        else:
            return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    AWAITING_PAYMENT = 'pre_payment'  # Customer has completed the checkout process, but payment has yet to be confirmed.
    PROCESSING = 'processing'  # Customer has completed the checkout process and payment has been confirmed.
    SHIPPED = 'shipped'  # Order has been shipped, but receipt has not been confirmed yet.
    COMPLETED = 'completed'  # Order has been shipped/picked up, and receipt is confirmed.
    CANCELLED = 'cancelled'  # The order has been cancelled by either the customer or the seller

    STATUS_CHOICES = (
        (AWAITING_PAYMENT, 'Awaiting payment'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled')
    )

    date = models.DateField(auto_now_add=True)
    status = models.CharField(STATUS_CHOICES, max_length=max(len(s[0]) for s in STATUS_CHOICES),
                              help_text="The current status of the order")
    items = models.ManyToManyField(to='Item', through='OrderItem', help_text="Items that the order comprises")
    customer = models.ForeignKey(to='Customer', on_delete=models.CASCADE,
                                 help_text="Customer that have made this order")

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    """
    Intermediary table between Order and Item tables.
    """
    item = models.ForeignKey(to='Item', on_delete=models.CASCADE)
    order = models.ForeignKey(to='Order', on_delete=models.CASCADE)
    n_pieces = models.PositiveIntegerField(help_text="Number of ordered item pieces")

    def __str__(self):
        return f"{self.n_pieces} pieces of {self.item}"


POSTAL_CODE_PATTERN = re.compile(r'\d{2}-\d{3}')


def validate_postal_code(postal_code):
    if POSTAL_CODE_PATTERN.match(postal_code) is None:
        raise ValidationError('Postal code must be in format XX-XXX where Xs are digits.')


def validate_city_name(city):
    if not city.isalpha():
        raise ValidationError("City name can only contain letters!")


class Address(models.Model):
    country = models.CharField(max_length=60, default='Poland')
    city = models.CharField(max_length=60, validators=[validate_city_name])
    postal_code = models.CharField(max_length=6, validators=[validate_postal_code])
    street = models.CharField(max_length=60)
    street_number = models.CharField(max_length=5)
    local_number = models.CharField(max_length=5)

    class Meta:
        verbose_name_plural = "Addresses"
