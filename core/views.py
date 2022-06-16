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
from django.conf import settings
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


def calc_total_cart_price(cart_item_list):
    total_price = sum(cart_item.item.price_sale * cart_item.n_pieces if cart_item.item.price_sale is not None
                      else cart_item.item.price * cart_item.n_pieces
                      for cart_item in cart_item_list)
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

        total_price = calc_total_cart_price(cart_item_list)

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


class CategoryFilteredView(ItemListView):
    model = Item
    template_name = "core/category.html"
    context_object_name = "item_list"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_name"] = SubCategory.objects.get(pk=self.kwargs['pk']).name
        return context

    def get_queryset(self):
        """
        Filter items on subcategory id.
        """
        return self.model.objects.filter(subcategories=self.kwargs['pk'])


class CheckoutView(View):
    template_name = "core/checkout.html"

    def get(self, request):
        cart = get_or_create_cart(request)[0]
        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        total_price = calc_total_cart_price(cart_item_list)

        form = CheckoutForm()
        context = {"cart_item_list": cart_item_list, "total_price": total_price, "form": form}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request):
        cart, cart_created = get_or_create_cart(request)
        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        if cart_created or len(cart_item_list) < 1:
            raise Http404("Koszyk jest pusty!")

        form = CheckoutForm(data=request.POST)

        if form.is_valid():
            address, address_created = Address.objects.get_or_create(**form.cleaned_data)
            user = request.user

            if user.is_authenticated:
                order = Order(user=user, address=address)
            else:
                order = Order(address=address)

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
                ordered_item.save() # TODO django.core.exceptions.ValidationError: {'order': ['To pole nie może być puste.']}
                Item.objects.get(pk=ordered_item.item.pk).in_stock -= ordered_item.n_pieces

            # remove items from cart
            for cart_item in cart_item_list:
                cart_item.delete()

            messages.add_message(request, level=messages.SUCCESS, message="Zamówienie wykonane pomyślnie!")
            return redirect(to=reverse('core:index'))

        # if form is invalid, show errors to the user
        else:
            total_price = calc_total_cart_price(cart_item_list)
            return render(request, template_name=self.template_name,
                          context={'cart_item_list': cart_item_list, 'total_price':total_price, 'form': form})


class UserView(View):

    def get(self, request):
        user = request.user

        if hasattr(user, "customer"):
            customer = user.customer
            customer_form = CustomerForm(instance=customer)
            logging.debug(customer)
        else:
            customer = None
            customer_form = CustomerForm()

        orders = Order.objects.filter(user=user).order_by("-date")
        context = {"user": user, "customer": customer, "customer_form": customer_form, "orders": orders}

        return render(request, template_name="core/user.html", context=context)

    def post(self, request):
        """
        POST method allows the customer to change his data.
        """
        user = request.user

        if hasattr(user, "customer"):
            customer = user.customer
            customer_form = CustomerForm(instance=customer, data=request.POST)
            logging.debug(customer)
        else:
            raise Http404("Klient nie istnieje")

        if customer_form.is_valid():
            customer_form.save()
            messages.add_message(request, level=messages.SUCCESS, message="Dane klienta zaktualizowane")
            return redirect(to=request.path)
        else:
            orders = Order.objects.filter(user=user).order_by("-date")
            context = {"user": user, "customer": customer, "customer_form": customer_form, "orders": orders}
            return render(request, template_name="core/user.html", context=context)







