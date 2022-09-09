from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from nucleus.models import User, Vendor, ActiveManager, InactiveManager


# Create your models here.

class ActiveOrder(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_checked_out=False)


class InactiveOrder(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_checked_out=True)


class Reviewed(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_reviewed=True)


class NotReviewed(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_reviewed=False)


class NotMoved(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_moved=False)


class Labels(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Product(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=2000)
    price = models.FloatField()
    discount = models.PositiveIntegerField(null=True, blank=True, default=0,
                                           help_text="Amount to be removed from ORIGINAL PRICE"
                                           )
    description = models.TextField(help_text="write the description in bullet points")
    specifications = models.TextField(null=True, blank=True, help_text="write the specifications in bullet points")
    key_features = models.TextField(null=True, blank=True, help_text="write the key-features, defining each key factor"
                                                                     "in bullet points")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, default="Vilgax Store")
    labels = models.ManyToManyField(Labels, blank=True)
    picture_of_product_1 = models.ImageField(upload_to="product_images")
    picture_of_product_2 = models.ImageField(upload_to="product_images", blank=True)
    picture_of_product_3 = models.ImageField(upload_to="product_images", blank=True)
    picture_of_product_4 = models.ImageField(upload_to="product_images", blank=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    class Meta:
        unique_together = ("name", "description", 'vendor')

    def __str__(self):
        return self.name

    def get_category(self):
        return self.sub_category.category

    def get_price_discount_percentage(self):
        return int(round((self.discount / self.price) * 100))

    def get_real_price(self):
        try:
            return abs(self.price - self.discount)
        except:
            return self.price


class OrderedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.CharField(max_length=500, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_moved = models.BooleanField(default=False)
    is_checked_out = models.BooleanField(default=False)
    date_checked_out = models.DateField(blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveOrder()
    inactive_objects = InactiveOrder()
    reviewed_objects = Reviewed()
    not_reviewed_objects = NotReviewed()
    not_moved_objects = NotMoved()

    class Meta:
        # unique_together = ("user", "product", "quantity", "is_moved")
        ordering = ("date_checked_out",)

    def __str__(self):
        return self.product.name

    def individual_product_price(self):
        return abs(self.product.get_real_price() * self.quantity)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.CharField(max_length=500, blank=True)
    ordered_products = models.ManyToManyField(OrderedProduct, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_checked_out = models.DateTimeField(null=True, blank=True)
    is_checked_out = models.BooleanField(default=False)

    objects = models.Manager()
    active_objects = ActiveOrder()
    inactive_objects = InactiveOrder()

    def cart_number_of_items(self):
        return self.ordered_products.count()


class WishList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_products = models.ManyToManyField(Product)

    # def __str__(self):
    #     return self.items


class Feedback(models.Model):
    RATING_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    topic = models.CharField(max_length=20, null=True)
    comments = models.TextField()
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, null=True, blank=True)
    date_commented = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()


class Checkout(models.Model):
    DELIVERY_CHOICES = (
        ("D", "Door Delivery"),
        ("P", "Pick Up Station")
    )

    PAYMENT_CHOICES = (
        ("Pay On Delivery", "Pay On Delivery"),
        ("Pay With Card", "Pay With Card"),
        ("Credit Card", "Credit Card"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=50, help_text="name of recipient")
    address = models.CharField(max_length=5000)
    phone_number = PhoneNumberField(null=True)
    delivery = models.CharField(max_length=1, choices=DELIVERY_CHOICES, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, null=True)
    checkout_date = models.DateTimeField(auto_now_add=True)


class Report(models.Model):
    REASON_CHOICES = (
        ("Product appears to be a replica", "Product appears to be a replica"),
        ("Product Description Contains Inappropriate Information", "Product Description Contains Inappropriate "
                                                                   "Information"),
        ("Profile description contains misleading information", "Profile description contains misleading information"),
        ("Product is Illegal", "Product is Illegal")
    )

    COMPLAINANT_CHOICES = (
        ("individual", "individual"),
        ("organization", "organization")
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=20, null=True, help_text="Kindly fill in your organization name, if you"
                                                                     "are making the report on behalf of your "
                                                                     "organization")
    complainant_type = models.CharField(max_length=20, choices=COMPLAINANT_CHOICES, null=True)
    reason_for_report = models.CharField(max_length=100, choices=REASON_CHOICES, null=True)
    additional_details = models.TextField(blank=True)
    additional_file = models.FileField(upload_to="complaint_files", blank=True)
    email = models.EmailField(null=True)
    phone_number = PhoneNumberField(null=True)


class SponsoredPost(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(help_text="input amount of days , you would like to run it for")
