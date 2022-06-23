from django.test import TestCase
from .models import *
from .forms import *


class CustomerFormTests(TestCase):
    valid_date_of_birth = timezone.now() - timedelta(days=20 * 365)

    def test_customer_form_with_user_under_13(self):
        """
        Filling CustomerForm with birthdate indicating that the user is under 13
        makes the form invalid with proper error message.
        """
        too_young_date_of_birth = timezone.now() - timedelta(days=(13 * 365) - 1)
        form = CustomerForm(
            data=dict(
                first_name="Foo",
                last_name="Bar",
                date_of_birth=too_young_date_of_birth,
                phone_number="111222333",
                gender="m")
        )
        self.assertFalse(form.is_valid())
        self.assertIn(DATE_VALIDATION_ERRORS['too_young_error'].message, form.errors['date_of_birth'])

    def test_customer_form_with_invalid_length_phone_number(self):
        """
        Filling CustomerForm with phone number of length greater or lesser than 9
        makes the form invalid with proper error message.
        """
        eight_digit_phone_number = "11122233"
        ten_digit_phone_number = "1112223334"

        eight_digit_phone_number_form = CustomerForm(
            data=dict(
                first_name="Foo",
                last_name="Bar",
                date_of_birth=self.valid_date_of_birth,
                phone_number=eight_digit_phone_number,
                gender="m")
        )

        ten_digit_phone_number_form = CustomerForm(
            data=dict(
                first_name="Foo",
                last_name="Bar",
                date_of_birth=self.valid_date_of_birth,
                phone_number=ten_digit_phone_number,
                gender="m")
        )

        self.assertFalse(eight_digit_phone_number_form.is_valid())
        self.assertIn(PHONE_NUMBER_VALIDATION_ERRORS['len_error'].message,
                      eight_digit_phone_number_form.errors['phone_number'])

        self.assertFalse(ten_digit_phone_number_form.is_valid())
        # too long input violates max_length CharField parameter

    def test_customer_form_with_phone_number_containing_non_digits(self):
        """
        Filling CustomerForm with phone number containing characters other than digits
        makes the form invalid.
        """
        phone_number_with_non_digits = "111a22333"

        form = CustomerForm(
            data=dict(
                first_name="Foo",
                last_name="Bar",
                date_of_birth=self.valid_date_of_birth,
                phone_number=phone_number_with_non_digits,
                gender="m")
        )

        self.assertFalse(form.is_valid())
        self.assertIn(PHONE_NUMBER_VALIDATION_ERRORS['non_digits_error'].message,
                      form.errors['phone_number'])

    def test_customer_form_with_valid_inputs(self):
        """
        Filling CustomerForm with phone number of length 9 and date_of_birth that indicates
        the user is over 13 makes the form valid.
        """
        valid_phone_number = "111222333"
        form = CustomerForm(
            data=dict(
                first_name="Foo",
                last_name="Bar",
                date_of_birth=self.valid_date_of_birth,
                phone_number=valid_phone_number,
                gender="m")
        )

        self.assertTrue(form.is_valid())


class AddressFormTests(TestCase):

    def test_address_form_with_city_name_containing_non_alpha(self):
        """
        Filling AddressForm with city name containing non alpha characters
        makes the form invalid with proper error message.
        """
        invalid_city_names = ["W4rszawa", "Wa/rszawa"]

        for invalid_city_name in invalid_city_names:

            form = AddressForm(
                data=dict(
                    country="Poland",
                    city=invalid_city_name,
                    postal_code="12-345",
                    street="Piastowa",
                    street_number="5B")
            )

            self.assertFalse(form.is_valid())
            self.assertIn(CITY_NAME_VALIDATION_ERRORS['non_alpha'].message, form.errors['city'])

    def test_address_form_with_invalid_postal_code_pattern(self):
        """
        Filling AddressForm with postal code of pattern other than XX-XXX where Xs are digits
        makes the form invalid with proper error message.
        """
        invalid_postal_codes = ["123-45", "12345", "12-35a"]

        for invalid_postal_code in invalid_postal_codes:
            form = AddressForm(
                data=dict(
                    country="Poland",
                    city="Warszawa",
                    postal_code=invalid_postal_code,
                    street="Piastowa",
                    street_number="5B")
            )

            self.assertFalse(form.is_valid())
            self.assertIn(POSTAL_CODE_VALIDATION_ERRORS['wrong_pattern'].message, form.errors['postal_code'])

    def test_address_form_with_valid_inputs(self):
        """
        Filling AddressForm with postal code of pattern XX-XXX where Xs are digits
        and city name containing only alphas makes the form valid.
        """

        form = AddressForm(
            data=dict(
                country="Poland",
                city="Warszawa",
                postal_code="12-345",
                street="Piastowa",
                street_number="5B")
        )

        self.assertTrue(form.is_valid())
