from django import forms

from .models import Checkout, Report, Feedback


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Checkout
        exclude = ("user", "checkout_date",)


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ("product",)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ("user", "product", "date_commented", "is_active")
