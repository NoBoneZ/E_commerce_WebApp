from django import template

from main_store.models import Cart
register = template.Library()


@register.filter
def cart_items_count(request):
    if request.user.is_authenticated():
        selected_cart = Cart.active_objects.filter(user_id=request.user.id).first()
        return selected_cart.ordered_products.all().count()
    selected_cart = Cart.active_objects.filter(ip_address=request.META.get("ip_address"))
    return selected_cart.ordered_products.all().count()
