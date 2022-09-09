from django.contrib import admin

from .models import Product, OrderedProduct, Category, Cart, SubCategory, Labels, Feedback


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = (Product.get_category, "name", "price", "vendor")
    list_filter = ("price", "vendor", 'name',)


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", 'category')
    list_filter = ("category",)


class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address","product")


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", Cart.cart_number_of_items, "date_checked_out")


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "topic", "rating")


admin.site.register(Product, ProductAdmin)
admin.site.register(OrderedProduct, OrderedProductAdmin)
admin.site.register(Category)
admin.site.register(Cart, CartAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Labels)
admin.site.register(Feedback, FeedbackAdmin)
