from django.urls import path

from. import views


app_name = "admin_overwatch"

urlpatterns = [
    path("", views.index, name="index"),
    path("overwatch_signin/", views.overwatch_signin, name="overwatch_signin"),
    path("overwatch_signout/", views.overwatch_signout, name="overwatch_signout"),

    path("create_category/", views.create_category, name="overwatch_create_category"),
    path("create_sub_category/", views.create_sub_category, name="overwatch_create_sub_category"),

    path("create_product/", views.create_product, name='overwatch_create_product'),
    path("edit_product/<int:pk>/", views.edit_product, name="overwatch_edit_product"),
    path("delete_product/<int:pk>/", views.delete_product, name="overwatch_delete_product"),
    path("view_deleted_products/", views.DeletedProducts.as_view(), name="overwatch_view_deleted_products"),
    path("product_details/<int:pk>/", views.overwatch_product_details, name="overwatch_product_details"),
    path("global_sales/", views.global_sales, name="overwatch_global_sales")


]