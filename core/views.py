from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .models import Item, CartItem, Cart, Customer
from django.contrib import messages
from django.urls import reverse
from .forms import AddItemToCartForm
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
                                 message=f"{item.name} successfully added to the cart")

            return redirect(to=reverse('core:detail', kwargs={'pk': pk}))

        else:
            return render(request, template_name=self.template_name,
                          context={'item': item, 'form': form})


class CartView(View):
    template_name = 'core/cart.html'

    def get(self, request):
        cart, created = get_or_create_cart(request)

        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        total_price = sum(cart_item.item.price_sale * cart_item.n_pieces if cart_item.item.price_sale is not None
                          else cart_item.item.price * cart_item.n_pieces
                          for cart_item in cart_item_list)

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
                                 message=f"{str(cart_item)} successfully removed from the cart")
        except ObjectDoesNotExist:

            raise Http404("Item not in the cart")

        return redirect(to=reverse('core:cart'))
