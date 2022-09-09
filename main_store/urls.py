from django.urls import path

from . import views

app_name = "main_store"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/product_details/", views.product_details, name="product_details"),
    path("<int:pk>/product_details/make_report", views.make_report, name="make_report"),
    path("<int:pk>/add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("order_summary/", views.order_summary, name="order_summary"),
    path("<int:pk>/order_summary/<int:id>/remove_product", views.remove_from_cart, name="remove_from_cart"),
    path("<int:pk>/order_summary/<int:id>/reduce_quantity", views.reduce_quantity, name="reduce_quantity"),
    path("<int:pk>/order_summary/<int:id>/increase_quantity", views.increase_quantity, name="increase_quantity"),
    path("<int:pk>/save_product_wishlist/<int:id>", views.save_product, name="save_product"),
    path("<int:pk>/remove_product_wishlist/<int:id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("<int:pk>/check_out/", views.user_checkout, name="checkout"),

]
