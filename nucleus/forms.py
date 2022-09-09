from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from .models import User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
                   )


class MyUserEditForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ("date_joined", "last_login", "superuser_status", "staff_status", "is_active", "password",
                   "email", "password1", "password2", "username"
                   )



