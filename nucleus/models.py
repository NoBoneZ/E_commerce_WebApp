from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class InactiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)


class ActiveManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class StaffManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=True)


class User(AbstractUser):
    first_name = models.CharField(max_length=30, null=True, blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    username = models.CharField(max_length=19, unique=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to="user_profile_picture", default="avatar.svg")
    age = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(16)], null=True, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, )
    is_vendor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()
    staff_objects = StaffManager()


class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name_of_store = models.CharField(max_length=500, null=True)
    location_of_store = models.TextField()
    next_of_kin_name = models.CharField(max_length=200)
    next_of_kin_address = models.TextField()
    next_of_kin_phone_number = PhoneNumberField(unique=True)
    followers = models.ManyToManyField(User, related_name="vendor_followers")


class Inbox(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(null=True, max_length=70)
    inbox = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
