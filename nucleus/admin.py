from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import MyUserCreationForm
from .models import User, Vendor, Inbox


# Register your models here.

class MyUserAdmin(UserAdmin):
    class Meta:
        form = MyUserCreationForm

        fieldsets = (('Main Information', {"fields": ("first_name", "middle_name", "last_name", "profile_picture", "phone_number")}),
                     ("addresses", {"fields": ("email", "address")}),
                     ("others", {"fields": ("age", "last_login")})
                     )

        list_display = ["first_name", "last_name", "email"]
        list_filter = ["age"]
        ordering = ["first_name"]


admin.site.register(User, MyUserAdmin)
admin.site.register(Vendor)
admin.site.register(Inbox)