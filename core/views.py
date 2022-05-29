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


class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'core/index.html'
    context_object_name = 'item_list'

    def get_queryset(self):
        """
        Sorting items alphabetically.
        """
        return self.model.objects.all().order_by('name')


class ItemDetailView(LoginRequiredMixin, View):
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

        customer = get_object_or_404(Customer, user=request.user)
        # get current customer's Cart instance or create one
        cart, created = Cart.objects.get_or_create(customer=customer)
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


class CartView(LoginRequiredMixin, View):
    template_name = 'core/cart.html'

    def get(self, request):
        cart = Cart.objects.get_or_create(customer=request.user.customer)[0]
        cart_item_list = CartItem.objects.filter(cart=cart).order_by('item__name')

        total_price = sum(cart_item.item.price_sale * cart_item.n_pieces if cart_item.item.price_sale is not None
                          else cart_item.item.price * cart_item.n_pieces
                          for cart_item in cart_item_list)

        context = {'cart_item_list': cart_item_list, 'total_price': total_price}
        return render(request, template_name=self.template_name, context=context)


class RemoveFromCartView(LoginRequiredMixin, View):

    def post(self, request, pk):
        cart, created = Cart.objects.get_or_create(customer=request.user.customer)
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
