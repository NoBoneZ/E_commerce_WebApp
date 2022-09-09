from django.shortcuts import render, reverse, get_object_or_404
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView

from nucleus.models import User, Vendor
from main_store.models import Category, SubCategory, Labels, Product, OrderedProduct, Cart, Report, Feedback
from .forms import ProductEditForm, CategoryEditForm, SubcategoryEditForm


# Create your views here.

@login_required(login_url="admin_overwatch:overwatch_signin")
def index(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    sales = []
    categories = Category.objects.all()

    search = request.GET.get("search") if request.GET.get("search") is not None else ""

    products = Product.active_objects.filter(
        Q(name__icontains=search) | Q(sub_category__category__name__icontains=search)
        # | Q(vendor__name_of_store=search) | Q(sub_category__icontains=search)
    )

    checked_out_carts = Cart.inactive_objects.all()

    for carts in checked_out_carts:
        for goods in carts.ordered_products.all():
            sales.append(goods)

    context = {
        "categories": categories,
        "products": products,
        "sales": sales,
    }

    return render(request, "admin_overwatch/overwatch_index.html", context)


def overwatch_signin(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # try:
        #     user = User.staff_objects.get(email=email)
        # except ObjectDoesNotExist:
        #     pass

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("admin_overwatch:index"))
        messages.error(request, "Invalid details")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    context = {
        "page": "sign_in",

    }
    return render(request, "admin_overwatch/overwatch_forms.html", context)


def overwatch_signout(request):
    logout(request)
    return HttpResponseRedirect(reverse("main_store:index"))


@login_required(login_url="admin_overwatch:overwatch_signin")
def overwatch_product_details(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    product_sales = []
    total_quantity = 0
    total_sold = 0
    product = Product.active_objects.get(id=pk)
    sold_carts = Cart.inactive_objects.all()

    for carts in sold_carts:
        for goods in carts.ordered_products.all():
            if goods.product.id == pk:
                product_sales.append(goods)
                total_quantity += goods.quantity
                total_sold += goods.individual_product_price()
    context = {
        "product": product,
        "product_sales": product_sales,
        "total_quantity": total_quantity,
        "total_sold": total_sold
    }

    return render(request, "admin_overwatch/overwatch_product_detail.html", context)


@login_required(login_url="admin_overwatch:overwatch_signin")
def edit_product(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    product = get_object_or_404(Product, id=pk)
    form = ProductEditForm(instance=product)
    page = "create_edit"

    if request.method == "POST":
        form = ProductEditForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()

            messages.success(request, f"{product.name} edited successfully")
            return HttpResponseRedirect(reverse("admin_overwatch:overwatch_product_details", args=[pk]))
        messages.error(request, "invalid entry, kindly check the entry")

    context = {
        "form": form,
        "page": page
    }

    return render(request, "admin_overwatch/overwatch_forms.html", context)


@login_required(login_url="admin_overwatch:overwatch_signin")
def create_product(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    form = ProductEditForm()
    page = "create_edit"

    if request.method == "POST":
        form = ProductEditForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, f"Product created successfully")
            return HttpResponseRedirect(reverse("admin_overwatch:index"))
        messages.error(request, "Invalid Entry, Kindly check your form")
    context = {
        "form": form,
        "page": page
    }

    return render(request, "admin_overwatch/overwatch_forms.html", context)


@login_required(login_url="admin_overwatch:overwatch_signin")
def delete_product(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    product = Product.objects.get(id=pk)
    product.is_active = not product.is_active
    product.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="admin_overwatch:overwatch_signin")
def create_category(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    page = "create_edit"
    form = CategoryEditForm()

    if request.method == "POST":
        form = CategoryEditForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, "Category created successfully")
            return HttpResponseRedirect(reverse("admin_overwatch:index"))
        messages.error(request, "Error!! kindly check your Input")

    context = {
        "page": page,
        "form": form,
    }
    return render(request, "admin_overwatch/overwatch_forms.html", context)


@login_required(login_url="admin_overwatch:overwatch_signin")
def create_sub_category(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    page = "create_edit"
    form = SubcategoryEditForm()

    if request.method == "POST":
        form = SubcategoryEditForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, "Category created successfully")
            return HttpResponseRedirect(reverse("admin_overwatch:index"))
        messages.error(request, "Error!! kindly check your Input")

    context = {
        "page": page,
        "form": form,
    }
    return render(request, "admin_overwatch/overwatch_forms.html", context)


class DeletedProducts(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Product
    template_name = "admin_overwatch/overwatch_deleted_products.html"
    login_url = "admin_overwatch:overwatch_signin"

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Product.inactive_objects.all

    def get_context_data(self, *args, **kwargs):
        context = super(DeletedProducts, self).get_context_data(**kwargs)
        context["products"] = self.get_queryset()
        return context


@login_required(login_url="admin_overwatch:overwatch_signin")
def global_sales(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    sold_products = []
    total_quantity = 0
    total_amount = 0
    selected_carts = Cart.inactive_objects.all()
    for carts in selected_carts:
        for goods in carts.ordered_products.all():
            sold_products.append(goods)
            total_quantity += goods.quantity
            total_amount += goods.individual_product_price()

    context = {
        "sold_products": sold_products,
        "total_quantity": total_quantity,
        "total_amount": total_amount,
    }

    return render(request, "admin_overwatch/overwatch_global_sales.html", context)
