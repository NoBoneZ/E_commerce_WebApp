from main_store.models import Cart


def cart_items_count(request):
    if request.user.is_authenticated:
        try:
            selected_cart = Cart.active_objects.filter(user_id=request.user.id).first()
            cart_total = selected_cart.ordered_products.all().count()
            return {"cart_total": cart_total}
        except:
            return {"cart_total": 0}
    else:
        try:
            selected_cart = Cart.active_objects.filter(ip_address=request.META.get("ip_address")).first()
            cart_total = selected_cart.ordered_products.all().count()
            return {"cart_total": cart_total}
        except:
            return {"cart_total": 0}
