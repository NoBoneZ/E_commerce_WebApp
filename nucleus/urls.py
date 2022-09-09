from django.urls import path

from . import views

app_name = "nucleus"

urlpatterns = [
    path("sign_up/", views.sign_up, name="sign_up"),
    path("sign_in/", views.user_sign_in, name="sign_in"),
    path("sign_out/", views.user_sign_out, name="sign_out"),
    path("password_recovery/", views.recover_password, name="recover_password"),
    path("reset_password/password-token/<str:uid>/<str:token>", views.reset_password, name="reset_password"),

    path("profile/<int:pk>/", views.UserProfile.as_view(), name="profile"),
    path("profile/<int:pk>/update_details/", views.user_update_details, name="update_details"),
    path("profile/<int:pk>/change_password/", views.change_password, name="change_password"),
    path("profile/<int:pk>/close_account/", views.close_account, name="close_account"),
    path("profile/<int:pk>/wishlist/", views.user_wishlist, name="user_wishlist"),
    path("profile/<int:pk>/user_review/", views.user_review, name="user_review"),
    path("profile/<int:pk>/address_book/", views.UserAddress.as_view(), name="user_address"),
    path("profile/<int:pk>/inbox", views.UserInbox.as_view(), name="user_inbox"),
    path("profile/<int:pk>/my_orders", views.UserAllOrders.as_view(), name="user_all_orders"),
]
