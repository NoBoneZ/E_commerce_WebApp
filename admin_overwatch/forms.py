from django import forms

from main_store.models import Category, Labels, Product, Feedback, SubCategory


class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class ProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("is_active",)


class LabelEditForm(forms.ModelForm):
    class Meta:
        model = Labels
        fields = "__all__"


class SubcategoryEditForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = "__all__"

