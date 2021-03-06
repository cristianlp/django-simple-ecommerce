from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.generic import DeleteView, DetailView, FormView
from django.core.urlresolvers import reverse_lazy
from .models import Cart, CartItem
from .mixins import get_cart
from products.models.product import Product
from .forms import AddToCartForm


class CartView(DetailView, FormView):
    model = Cart
    template_name = "cart_index.html"

    def get(self, *args, **kwargs):
        cart = get_cart(self.request)
        return render(self.request, template_name=self.template_name, context={'cart': cart})


# Removing item from cart
class RemoveCartItemView(DeleteView):
    model = CartItem
    success_url = reverse_lazy('cart:index')
    success_message = "The item has been deleted from your cart."
    http_method_names = ['post']

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(RemoveCartItemView, self).delete(self.request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        cart = get_cart(self.request)
        return CartItem.objects.get(cart=cart, product_id=self.kwargs['product_id'])


class UpdateCartItemView(FormView):
    http_method_names = ['post']
    success_url = reverse_lazy('cart:index')
    form_class = AddToCartForm
    template_name = 'cart_index.html'
    context_object_name = 'cart'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        cart = get_cart(request)
        cart_item = CartItem.objects.get(cart=cart, product_id=self.kwargs['product_id'])
        cart_item.quantity = request.POST['cart_item_quantity']
        cart_item.save()
        return self.form_valid(form)

    def form_valid(self, form, *args, **kwargs):
        messages.success(self.request, "Product quantity has been updated.")
        return super(UpdateCartItemView, self).form_valid(form)


class AddToCartView(FormView):
    template_name = 'product_detail.html'
    success_url = reverse_lazy('cart:index')
    http_method_names = ['post']
    form_class = AddToCartForm

    def form_valid(self, form, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        quantity = form.cleaned_data['quantity']

        cart = get_cart(self.request)
        cart_item, cart_item_created = CartItem.objects.update_or_create(cart=cart, product=product)

        # If Cart item object has not been created  , amend quantity.
        if cart_item_created is False:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        return super(AddToCartView, self).form_valid(form)
