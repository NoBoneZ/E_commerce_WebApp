from math import fsum

from datetime import date, datetime
from random import shuffle, sample

from django.db.models import Q
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, View
from django.contrib.sessions.backends.db import SessionStore

from .models import Category, Product, OrderedProduct, Cart, WishList, Checkout, Feedback
from .forms import CheckoutForm, ReportForm


# Create your views here.


def get_cart_total(pk):
    cart = Cart.active_objects.filter(user_id=pk).first()
    ordered_products = cart.ordered_products.all()
    prices = 0

    for product in ordered_products:
        prices += product.product.get_real_price() * product.quantity

    return prices


def index(request):
    sales = []
    hot_deals = []
    categories_for_recommendation = []
    recommended_products_list = []

    categories = Category.objects.all()

    search = request.GET.get("search") if request.GET.get("search") is not None else ""

    products = Product.active_objects.filter(
        Q(name__icontains=search) | Q(sub_category__category__name__icontains=search))

    all_settled_carts = Cart.inactive_objects.all()

    for cart in all_settled_carts:
        for goods in cart.ordered_products.all():
            sales.append(goods)

    hot_products = Product.active_objects.all()
    for selected_product in hot_products:
        if selected_product.get_price_discount_percentage() > 0:
            hot_deals.append(selected_product)

    try:
        wish_recommended_for_you = WishList.objects.get(user_id=request.user.id).saved_products.all()
        for recommended_goods in wish_recommended_for_you:
            categories_for_recommendation.append(recommended_goods.get_category())
    except:
        pass

    for merchandise in Product.objects.all():
        if merchandise.get_category() in categories_for_recommendation and merchandise not in wish_recommended_for_you:
            recommended_products_list.append(merchandise)

    context = {
        "categories": categories,
        "products": products,
        "sales": sales,
        "hot_deals": hot_deals[:5],
        "recommended_products": recommended_products_list[:5]
    }
    return render(request, "main_store/index.html", context)


def add_to_cart(request, pk):
    if request.user.is_authenticated:
        marked_product = Product.objects.get(id=pk)
        ordered_product, created = OrderedProduct.not_moved_objects.get_or_create(user=request.user,
                                                                                  product=marked_product)
        selected_cart = Cart.active_objects.filter(user=request.user).first()

        if selected_cart is not None:
            if ordered_product in selected_cart.ordered_products.all():
                ordered_product.quantity += 1
                ordered_product.save()
                messages.success(request, f'{ordered_product} added successfully')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                selected_cart.ordered_products.add(ordered_product)
                messages.success(request, f'{ordered_product} added successfully')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
        else:
            new_cart = Cart.objects.create(user=request.user, )
            new_cart.ordered_products.add(ordered_product)
            new_cart.save()
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    else:
        marked_product = Product.objects.get(id=pk)
        ordered_product, created = OrderedProduct.not_moved_objects.get_or_create(
            ip_address=request.META.get("REMOTE_ADDR"),
            product=marked_product
        )
        selected_cart = Cart.active_objects.filter(ip_address=request.META.get("REMOTE_ADDR")).first()

        if selected_cart is not None:
            if ordered_product in selected_cart.ordered_products.all():
                ordered_product.quantity += 1
                ordered_product.save()
                messages.success(request, f'{ordered_product} added successfully using address')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            else:
                selected_cart.ordered_products.add(ordered_product)
                messages.success(request, f'{ordered_product} added successfully using address')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        else:
            new_cart = Cart.objects.create(ip_address=request.META.get("REMOTE_ADDR"))
            new_cart.ordered_products.add(ordered_product)
            new_cart.save()
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="nucleus:sign_in")
def remove_from_cart(request, pk, id):
    if request.user.id != pk:
        return HttpResponseForbidden()

    selected_cart = Cart.active_objects.filter(user_id=pk).first()
    selected_product = OrderedProduct.not_moved_objects.filter(user_id=pk, product_id=id).first()

    selected_cart.ordered_products.remove(selected_product)
    selected_product.save()

    selected_product.quantity = 1
    selected_product.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="nucleus:sign_in")
def order_summary(request):
    # if request.user.id != pk:
    #     return HttpResponseForbidden()

    selected_cart = Cart.active_objects.filter(user_id=request.user.id).first()

    try:
        user_wishlist = WishList.objects.get(user_id=request.user.id)
        selected_wishlist = user_wishlist.saved_products.all()[:5]
    except:
        selected_wishlist = []

    if selected_cart is not None:
        ordered_products = selected_cart.ordered_products.all()

        context = {
            "ordered_products": ordered_products,
            "cart": selected_cart,
            "total": get_cart_total(request.user.id),
            "wishlist": selected_wishlist,
        }
        return render(request, "main_store/cart_summary.html", context)
    else:
        messages.error(request, "Cart is empty")
        return HttpResponseRedirect(reverse("main_store:index"))


@login_required(login_url="nucleus:sign_in")
def reduce_quantity(request, pk, id):
    if request.user.id != pk:
        return HttpResponseForbidden()

    selected_product = OrderedProduct.not_moved_objects.filter(user_id=pk, product_id=id).first()
    if selected_product.quantity > 1:
        selected_product.quantity -= 1
        selected_product.save()
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    messages.error(request, f"{selected_product} quantity can't go below 1, You could remove it instead ")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="nucleus:sign_in")
def increase_quantity(request, pk, id):
    if request.user.id != pk:
        return HttpResponseForbidden()

    selected_product = OrderedProduct.not_moved_objects.filter(user_id=pk, product_id=id).first()
    selected_product.quantity += 1
    selected_product.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="nucleus:sign_in")
def save_product(request, pk, id):
    user_wishlist, created = WishList.objects.get_or_create(user_id=pk)
    product = Product.objects.get(id=id)

    if product not in user_wishlist.saved_products.all():
        user_wishlist.saved_products.add(product)
        messages.error(request, f"{product.name} saved in wish list")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    user_wishlist.saved_products.remove(product)
    messages.error(request, f"{product.name} removed from wish list")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="nucleus:sign_in")
def user_checkout(request, pk):
    if request.user.id != pk:
        return HttpResponseForbidden()

    # TRY AND APPLY TIMEDELTA AMD TIMEZONE
    form = CheckoutForm()
    selected_cart = Cart.active_objects.filter(user_id=pk).first()
    products = selected_cart.ordered_products.all()
    total = get_cart_total(pk)
    page = "checkout_form"

    if len(products) == 0:
        messages.error(request, "Cart is empty")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    if request.method == "POST":
        form = CheckoutForm(request.POST, request.FILES)
        print(form.errors)

        if form.is_valid():
            checkout = form.save(commit=False)
            checkout.user = request.user
            checkout.save()

            selected_cart.is_checked_out = True
            selected_cart.date_checked_out = datetime.now()
            selected_cart.save()

            for product in products:
                product.is_checked_out = True
                product.date_checked_out = date.today()
                product.save()

            messages.success(request, "Your goods will be delivered to you within 3 working days")
            return HttpResponseRedirect(reverse("main_store:index"))

        messages.error(request, "kindly check the form, invalid details")

    context = {
        "form": form,
        "products": products,
        "total": total,
        "page": page,
    }
    return render(request, "main_store/store_forms.html", context)


@login_required(login_url="nucleus:sign_in")
def product_details(request, pk):
    rating_list = []
    product = Product.objects.get(id=pk)
    feedback = Feedback.objects.filter(product_id=pk)

    for rating in feedback:
        rating_list.append(int(rating.rating))

    try:
        average_rating = fsum(rating_list) / len(rating_list)
    except ZeroDivisionError:
        average_rating = None

    recently_viewed_products = None

    if "recently_viewed" in request.session:
        if product.id in request.session["recently_viewed"]:
            request.session["recently_viewed"].remove(product.id)
        recently_viewed_products = Product.active_objects.filter(pk__in=request.session["recently_viewed"])
        request.session["recently_viewed"].insert(0, product.id)
        if len(request.session["recently_viewed"]) > 6:
            request.session["recently_viewed"].pop()

    else:
        request.session["recently_viewed"] = [product.id]

    request.session.modified = True

    context = {
        "product": product,
        "feedback": feedback,
        "rating": average_rating,
        "recently_viewed_products": recently_viewed_products,
    }

    return render(request, "main_store/product_detail.html", context)


def make_report(request, pk):
    product = Product.objects.get(id=pk)
    form = ReportForm()

    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save(commit=False)
            report.product = product
            report.save()
            messages.success(request, f"Report on {product.name} made successfully")
            return HttpResponseRedirect(reverse("main_store:item_details", args=[pk]))
        messages.error(request, "Error!!, Kindly check your input")

    context = {
        "product": product,
        "form": form,
        "page": "complaint_form",
    }

    return render(request, "main_store/store_forms.html", context)


@login_required(login_url="nucleus:sign_in")
def remove_from_wishlist(request, pk, id):
    user_wishlist = WishList.objects.get(user_id=pk)
    product = Product.objects.get(id=id)

    user_wishlist.saved_products.remove(product)
    user_wishlist.save()

    messages.success(request, f"{product.name} removed successfully !")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
