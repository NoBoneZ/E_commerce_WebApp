import math

from django.shortcuts import render, reverse
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import DetailView, ListView
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from .forms import MyUserCreationForm, MyUserEditForm
from .models import User, Inbox
from main_store.models import WishList, Cart, Checkout, Product, OrderedProduct
from main_store.forms import FeedbackForm


# Create your views here.

class UserIsNotOwnerMixIn(UserPassesTestMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.id == kwargs['pk']:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


# def send_email_func(email_body: dict):
#     try:
#         html = render_to_string('accounts/mail_body.html', {"message:email_body['messages']})
#         subject = email_body["subject"]
#         email_from = settings.EMAIL_HOST_USER
#         recipient_list = email_body["recipients]
#
#         mail = EmailMessage(subject, email_body["messages"], to=[recipient_list])
#         mail.send()
#         return True
#
#     except Exception as e:
#         print(e)
#         return

def user_sign_in(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    page = "sign_in"

    if request.method == "POST":
        try:
            user = User.active_objects.get(email=email)

        except:
            messages.error(request, "Email does not exist, you should probably sign up or check your e-mail")
            return render(request, "nucleus/signin_signup.html", {"page": page})

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)

            address_cart = Cart.active_objects.filter(ip_address=request.META.get("REMOTE_ADDR")).first()
            selected_cart = Cart.active_objects.filter(user_id=user.id).first()
            # print(selected_cart.ordered_products.all())

            if address_cart is not None:
                if selected_cart is not None:
                    for good in address_cart.ordered_products.all():
                        for merch in selected_cart.ordered_products.all():
                            print(merch.product)
                            # if merch.product.id == good.product.id:
                            #     print(good.id)
                            #     print(merch.id)
                            #     merch.id, good.id = good.id, merch.id
                            #     merch.quantity += good.quantity
                            #     merch.save()
                            #     # good.is_moved = True
                            #     good.delete()


                        else:
                            good.user = User.active_objects.get(id=request.user.id)
                            # good.is_moved = True
                            good.save()
                            selected_cart.ordered_products.add(good)
                            selected_cart.save()



                else:
                    selected_cart = Cart.objects.create(user_id=request.user.id)
                    selected_cart.save()
                    for good in address_cart.ordered_products.all():
                        good.user = User.active_objects.get(id=request.user.id)
                        # good.is_moved = True
                        good.save()
                        selected_cart.ordered_products.add(good)
                        selected_cart.save()

                selected_cart.save()
                # address_cart.is_checked_out = True
                address_cart.delete()

            return HttpResponseRedirect(reverse("main_store:index"))
        messages.error(request, "Invalid login details")
        return render(request, "nucleus/signin_signup.html", {"page": page})

    elif request.method == "GET":
        return render(request, "nucleus/signin_signup.html", {"page": page})


def user_sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("main_store:index"))


def sign_up(request):
    form = MyUserCreationForm()
    page = "sign_up"

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, )

        if form.is_valid():
            my_user = form.save(commit=False)
            my_user.is_active = True
            my_user.save()

            my_user = User.active_objects.get(email=request.POST.get("email"))
            login(request, my_user)
            return HttpResponseRedirect(reverse("main_store:index"))
        messages.error(request, 'An error occurred during details entry, please check ')

    context = {
        "form": form,
        "page": page
    }

    return render(request, "nucleus/signin_signup.html", context)


class UserProfile(LoginRequiredMixin, AccessMixin, DetailView):
    model = User
    template_name = "nucleus/profile.html"
    context_object_name = 'user'
    login_url = "nucleus:sign_in"


@login_required(login_url="nucleus:sign_in")
def user_update_details(request, pk):
    if request.user.id != pk:
        return HttpResponseForbidden()

    user = User.active_objects.get(id=pk)
    form = MyUserEditForm(instance=user)
    page = "user_update_details"

    if request.method == "POST":
        form = MyUserEditForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()

            messages.success(request, "Profile updated Successfully !")
            return HttpResponseRedirect(reverse('nucleus:profile', args=[user.id]))

        else:
            print(form.errors)
            messages.error(request, 'Invalid detail entered')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    elif request.method == "GET":
        context = {
            "form": form,
            "page": page,
        }
        return render(request, "nucleus/profile_forms.html", context)


@login_required(login_url="nucleus:sign_in")
def change_password(request, pk):
    if request.user.id != pk:
        return HttpResponseForbidden()

    form = PasswordChangeForm(request.user)
    page = "change_password"

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password Changed Successfully")
            return HttpResponseRedirect(reverse("nucleus:profile", args=[pk]))
        else:
            messages.error(request, "please correct the error below")

    context = {"form": form,
               "page": page,
               }
    return render(request, "nucleus/profile_forms.html", context)


def close_account(request, pk):
    user = User.active_objects.get(id=pk)
    page = "close_account"

    if request.method == "POST":
        user.is_active = False
        user.save()

        logout(request)
        messages.success(request, "Account deleted Successfully")
        return HttpResponseRedirect(reverse("main_store:index"))

    context = {
        "page": page,
    }
    return render(request, "nucleus/profile_forms.html", context)


class UserWishlist(ListView):
    model = WishList
    template_name = "nucleus/profile_list.html"

    def get_queryset(self, **kwargs):
        selected_wishlist = WishList.objects.get(user_id=self.kwargs["pk"])
        return selected_wishlist.saved_products.all()

    def get_context_data(self, **kwargs):
        context = super(UserWishlist, self).get_context_data(**kwargs)
        context["wishlist"] = self.get_queryset()
        context["page"] = "wish_list"
        return context


@login_required(login_url="nucleus:sign_in")
def user_wishlist(request, pk):
    if request.user.id != pk:
        return HttpResponseForbidden()

    try:
        selected_wishlist = WishList.objects.get(user_id=pk)
    except Exception as e:
        messages.info(request, "Empty Wishlist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    wishlist = selected_wishlist.saved_products.all()
    page = "wishlist"

    context = {
        "wishlist": wishlist,
        "page": page
    }
    return render(request, "nucleus/profile_list.html", context)


@login_required(login_url="nucleus:sign_in")
def user_review(request, pk):
    if request.user.id != pk:
        return HttpResponseForbidden()

    products = []
    selected_carts = Cart.inactive_objects.filter(user_id=pk)
    for carts in selected_carts:
        for goods in carts.ordered_products.all():
            if not goods.is_reviewed:
                products.append(goods)

    page = "rate_review"
    form = FeedbackForm()

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            user = User.active_objects.get(id=pk)
            product = Product.active_objects.get(id=request.POST.get("product"))
            print(user.id)
            print(product.id)
            reviewed_product = OrderedProduct.inactive_objects.filter(user_id=user.id, product_id=product.id).first()
            reviewed_product.is_reviewed = True
            reviewed_product.save()

            feed = form.save(commit=False)
            feed.user = User.active_objects.get(id=pk)
            print(feed.user)
            feed.product = Product.active_objects.get(id=request.POST.get("product"))
            print(feed.product)
            feed.save()

            messages.success(request, "Review Received !")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        messages.error(request, "Invalid Entry, Kindly check the fields")

    context = {
        "products": products,
        "form": form,
        "page": page
    }
    return render(request, "nucleus/profile_forms.html", context)


class UserAddress(LoginRequiredMixin, ListView):
    model = Checkout
    template_name = "nucleus/profile_list.html"
    login_url = "nucleus:sign_in"

    def get_queryset(self, **kwargs):
        return Checkout.objects.filter(user_id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UserAddress, self).get_context_data(**kwargs)
        context["addresses"] = self.get_queryset()
        context["page"] = "address"
        return context


class UserInbox(LoginRequiredMixin, ListView):
    model = Inbox
    template_name = "nucleus/profile_list.html"
    login_url = "nucleus:sign_in"

    def get_queryset(self, **kwargs):
        return Inbox.objects.filter(user_id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UserInbox, self).get_context_data(**kwargs)
        context["messages"] = self.get_queryset()
        context["page"] = "inbox"
        return context


class UserAllOrders(LoginRequiredMixin, ListView):
    model = Cart
    login_url = "nucleus:sign_in"
    template_name = "nucleus/profile_list.html"

    def get_queryset(self):
        return Cart.inactive_objects.filter(user_id=self.kwargs["pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        amount_spent = []
        bought_goods = []
        for cart in self.get_queryset():
            for goods in cart.ordered_products.all():
                bought_goods.append(goods)
                amount_spent.append(goods.individual_product_price())

        context = super(UserAllOrders, self).get_context_data(**kwargs)
        context["amount_spent"] = math.fsum(amount_spent)
        context["bought_goods"] = bought_goods
        context["page"] = "orders"
        return context


def recover_password(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email")
            user = User.active_objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)

            email_body = {
                'token': token,
                "subject": "Recover Password",
                'message': f"Hi, {user.username} , kindly reset your password by clicking "
                           f"the following link . http://{current_site}/accounts/reset_password/password-token/{uid}/{token} "
                           f"to change your password",
                "recepient": email,
            }
            # that send email func
            send_mail(
                email_body["subject"],
                email_body["message"],
                settings.EMAIL_HOST_USER,
                [email]

            )
            print(email_body["message"])
            messages.success(request, "A password reset mail has been sent to your mail")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except User.DoesNotExist or Exception as e:
            print(e)
            messages.error(request, "User does not exist")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {
        'page': "recover_password",
    }
    return render(request, "nucleus/signin_signup.html", context)


def reset_password(request, uid, token):
    if request.method == "POST":
        try:
            id_decode = urlsafe_base64_decode(uid)
            user = User.active_objects.get(id=id_decode)

            if default_token_generator.check_token(user, token):
                password = request.POST.get("password1")
                confirm_password = request.POST.get("password1")

                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    messages.success(request, "password Recovered successfully")
                    return HttpResponseRedirect(reverse("main_store:index"))
                messages.error(request, "incorrect passwords")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

            else:
                messages.error(request, "Invalid Token")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        except:
            messages.error(request, "Invalid link")
            return HttpResponseRedirect("nucleus:sign_in")

    context = {
        'page': "reset_password",
        "uid": urlsafe_base64_decode(uid),
        "token": User.active_objects.get(id=urlsafe_base64_decode(uid)),

    }
    return render(request, "nucleus/signin_signup.html", context)
