from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import *
from django.contrib import messages
from django.urls import reverse
from .forms import *
from django.core.validators import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.html import escape
from django.conf import settings
from django.db.models import Q
import logging


def get_or_create_cart(request):
    """
    Helper function for retrieving an existing Cart instance or creating a new one.
    :return: tuple(cart: Cart instance, created: boolean flag - True if new cart was created else False)
    """
    user = request.user
    session_key = request.session.session_key
    if session_key is None:
        # if session_key is None then session is not in database -> create new session and retrieve new session_key
        request.session.create()
        session_key = request.session.session_key

    if user.is_authenticated:
        # if user is logged in -> try to retrieve current Cart instance based on current session_key
        try:
            cart = Cart.objects.get(session=session_key)
            # cart assigned to session become associated with the logged-in user
            cart.user = user
            cart.save()
            created = False

        except ObjectDoesNotExist:
            # if the cart associated with session does not exist, try to get a Cart instance already associated with the user
            # or create a new Cart instance and bind it to the user
            cart, created = Cart.objects.get_or_create(user=user)
            # associate the current session with the cart
            cart.session = session_key
            cart.save()

    else:
        cart, created = Cart.objects.get_or_create(session=session_key)

        if settings.DEBUG:
            if not created:
                logging.debug("Cart fetched - session_id: " + session_key)
            else:
                logging.debug("Cart created - session_id: " + session_key)

    return cart, created


def calc_total_price(container_item_list):
    total_price = sum(
        container_item.item.price_sale * container_item.n_pieces if container_item.item.price_sale is not None
        else container_item.item.price * container_item.n_pieces
        for container_item in container_item_list)
    return total_price


class ItemListView(ListView):
    model = Item
    template_name = 'core/index.html'
    context_object_name = 'item_list'

    def get_queryset(self):
        return self.model.objects.all()[:4]


class KafelkiItemListView(ListView):
    model = Item
    template_name = 'core/kafelki.html'
    context_object_name = 'item_list'

    def get_queryset(self):
        return self.model.objects.all()


class ItemDetailView(View):
    template_name = 'core/item_detail.html'

    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        form = AddItemToCartForm()
        context = {'item': item, 'form': form}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, pk):
        """
        POST method allows for adding item to the cart.
        """
        item = get_object_or_404(Item, pk=pk)  # get item instance by primary key lookup
        form = AddItemToCartForm(request.POST)  # get user input from form

        cart, created = get_or_create_cart(request)
        # create CartItem instance and use it to bind the cart with the item
        if form.is_valid():
            try:
                if not created:
                    # if cart already exists
                    # increase CartItem n_pieces, else create a new CartItem instance
                    try:
                        # get CartItem instance if it's already in the cart
                        cart_item = CartItem.objects.get(cart=cart, item=item)
                    except ObjectDoesNotExist:
                        # create CartItem instance with 0 n_pieces if it's not in the cart yet
                        cart_item = CartItem(cart=cart, item=item, n_pieces=0)

                    # increase n_pieces in the CartItem instance based on user input
                    cart_item.n_pieces += form.cleaned_data.get('n_pieces')
                    # try to save the CartItem in the database (validator checks if current CartItem.n_pieces <= Item.in_stock)
                    cart_item.save()
                else:
                    # if cart was created then it's empty, and it's safe to also create CartItem instance
                    cart_item = CartItem.objects.create(cart=cart, item=item,
                                                        n_pieces=form.cleaned_data.get('n_pieces'))

            except ValidationError as ex:
                messages.add_message(request, level=messages.WARNING, message=ex.messages[0])

                return render(request, template_name=self.template_name,
                              context={'item': item, 'form': form})

            messages.add_message(request, level=messages.SUCCESS,
                                 message=f"Dodano do koszyka: {cart_item}")

            return redirect(to=reverse('core:detail', kwargs={'pk': pk}))

        else:
            return render(request, template_name=self.template_name,
                          context={'item': item, 'form': form})


class CartView(View):
    template_name = 'core/cart.html'

    def get(self, request):
        cart = get_or_create_cart(request)[0]

        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        total_price = calc_total_price(cart_item_list)

        context = {'cart_item_list': cart_item_list, 'total_price': total_price}
        return render(request, template_name=self.template_name, context=context)


class RemoveFromCartView(View):

    def post(self, request, pk):
        cart, created = get_or_create_cart(request)

        if created:
            raise Http404("Item not in the cart")

        try:
            cart_item = CartItem.objects.get(cart=cart, item__pk=pk)
            cart_item.delete()
            messages.add_message(request, level=messages.SUCCESS,
                                 message=f"Usunięto z koszyka: {cart_item}")
        except ObjectDoesNotExist:

            raise Http404("Item not in the cart")

        return redirect(to=reverse('core:cart'))


class CategoryFilteredView(View):
    template_name = "core/category.html"

    def get(self, request, pk):
        """
        Filter items on subcategory id and price range.
        """
        category_name = get_object_or_404(SubCategory, pk=pk).name
        context = {'category_name': category_name}

        min_price = request.GET.get('min-price', False)
        max_price = request.GET.get('max-price', False)
        logging.debug(min_price)
        logging.debug(max_price)
        if min_price and max_price:
            # if user selected the minimal and maximal product price -> filter product list by subcategory and price range
            item_list = Item.objects.filter(
                Q(subcategories=pk) & (
                        Q(price_sale__isnull=False) & Q(price_sale__gte=min_price) & Q(price_sale__lte=max_price) |
                        Q(price_sale__isnull=True) & Q(price__gte=min_price) & Q(price__lte=max_price)
                )

            )
            # min_price and max_price are user inputs rendered directly in the page - html escaping will prevent XSS attack
            context['min_price'] = escape(min_price)
            context['max_price'] = escape(max_price)
        else:
            item_list = Item.objects.filter(subcategories=pk)
            # set default price range to render on price range sliders
            context['min_price'] = 0
            context['max_price'] = 100

        context['item_list'] = item_list

        return render(request, self.template_name, context=context)


class CheckoutView(View):
    """
    Checkout view for finalizing the order.
    """

    template_name = "core/checkout.html"

    def get(self, request):
        cart = get_or_create_cart(request)[0]
        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        total_price = calc_total_price(cart_item_list)

        user = request.user
        # check if user is logged in and if user is a customer and if it has address bound to his account
        if user.is_authenticated and hasattr(user, "customer"):
            # pre-fill the checkout form with customer data
            customerForm = CustomerCheckoutForm(instance=user.customer)
            if hasattr(user.customer, "address"):
                customer_address = user.customer.address
                # pre-fill the checkout form with address bound to the customer (e.g. address used by the last checkout)
                form = AddressForm(instance=customer_address)
            else:
                form = AddressForm()
        else:
            form = AddressForm()
            customerForm = CustomerCheckoutForm()

        orderMethodsForm = OrderMethodsForm()

        context = {"cart_item_list": cart_item_list, "total_price": total_price, "form": form,
                   "customerForm": customerForm, "orderMethodsForm": orderMethodsForm}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        user = request.user
        cart, cart_created = get_or_create_cart(request)
        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        if cart_created or len(cart_item_list) < 1:
            raise Http404("Koszyk jest pusty!")

        # assign None to necessary variables
        customer = customerForm = customerForm_valid = None

        if hasattr(user, 'customer'):
            # if user is already a customer -> retrieve customer bound to the user from the database
            customer = user.customer
        else:
            # if user is not a customer yet (or the user is not logged in) -> use the CustomerCheckoutForm
            customerForm = CustomerCheckoutForm(data=request.POST)
            customerForm_valid = customerForm.is_valid()

        form = AddressForm(data=request.POST)
        orderMethodsForm = OrderMethodsForm(data=request.POST)
        if form.is_valid() and orderMethodsForm.is_valid():
            if not customer:
                if customerForm_valid:
                    customer, customer_created = Customer.objects.get_or_create(**customerForm.cleaned_data)
                else:
                    total_price = calc_total_price(cart_item_list)
                    return render(request, template_name=self.template_name,
                                  context={'cart_item_list': cart_item_list, 'total_price': total_price, 'form': form,
                                           'customerForm': customerForm, "orderMethodsForm": orderMethodsForm})

            address, address_created = Address.objects.get_or_create(**form.cleaned_data)
            customer.address = address
            if user.is_authenticated:
                customer.user = user
            customer.save()

            order = Order.objects.create(address=address, customer=customer,
                                         delivery_method=orderMethodsForm.cleaned_data.get("delivery_method"),
                                         payment_method=orderMethodsForm.cleaned_data.get("payment_method"))

            ordered_items = [OrderItem(order=order, item=cart_item.item, n_pieces=cart_item.n_pieces)
                             for cart_item in cart_item_list]
            try:
                # Check if all items that are about to be checked out have enough pieces in stock, if not show error
                for ordered_item in ordered_items:
                    ordered_item.validate_enough_pieces()

            except ValidationError as ex:
                # If the pharmacy is short on at least one of items that are about to be checked out
                # (order_item.n_pieces > item.in_stock) -> show error message
                messages.add_message(request, level=messages.WARNING, message=ex.messages[0])
                return render(request, template_name=self.template_name, context={"form": form})

            # bind ordered items to order and adjust the item stock
            for ordered_item in ordered_items:
                ordered_item.save()
                item = Item.objects.get(pk=ordered_item.item.pk)
                item.in_stock -= ordered_item.n_pieces
                item.save()

            order.total_price = calc_total_price(ordered_items)
            order.save()

            # remove items from cart
            for cart_item in cart_item_list:
                cart_item.delete()

            messages.add_message(request, level=messages.SUCCESS, message=f"Zamówienie #{order.pk} wykonane pomyślnie!")
            return redirect(to=reverse('core:summary'))

        # if form is invalid, show errors to the user
        else:
            if customerForm is None:
                customerForm = CustomerCheckoutForm()
            total_price = calc_total_price(cart_item_list)
            messages.add_message(request, level=messages.WARNING, message=f"Proszę poprawić błędy w formularzu zamówienia")
            return render(request, template_name=self.template_name,
                          context={'cart_item_list': cart_item_list, 'total_price': total_price, 'form': form,
                                   'customerForm': customerForm, "orderMethodsForm": orderMethodsForm})


class UserView(View):

    def get(self, request):
        """
        GET method allows for displaying the form for editing the customer's personal data,
        as well as for viewing the user's history of transactions.
        """
        user = request.user

        if hasattr(user, "customer"):
            customer = user.customer
            initial_date_of_birth = customer.date_of_birth.isoformat()
            initial_data = {"date_of_birth": initial_date_of_birth}
            customer_form = CustomerForm(instance=customer, initial=initial_data)
            logging.debug(customer)
        else:
            customer = None
            customer_form = CustomerForm()

        email_form = EmailForm(instance=user)

        orders = Order.objects.filter(customer__user=user).order_by("-date")
        context = {"user": user, "customer": customer, "customer_form": customer_form, "orders": orders,
                   "email_form": email_form}

        return render(request, template_name="core/user.html", context=context)

    def post(self, request):
        """
        POST method allows the customer to change his data.
        """
        user = request.user

        if hasattr(user, "customer"):
            customer = user.customer
            customer_form = CustomerForm(instance=customer, data=request.POST)
            email_form = EmailForm(instance=user, data=request.POST)
            logging.debug(customer)
        else:
            raise Http404("Klient nie istnieje")

        if customer_form.is_valid() and email_form.is_valid():
            customer_form.save()
            email_form.save()
            messages.add_message(request, level=messages.SUCCESS, message="Dane klienta zaktualizowane")
            return redirect(to=request.path)
        else:
            orders = Order.objects.filter(customer__user=user).order_by("-date")
            context = {"user": user, "customer": customer, "customer_form": customer_form, "orders": orders}
            return render(request, template_name="core/user.html", context=context)
