from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    Registration form extending Django's UserCreationForm.

    Adds email, first_name, last_name, phone and country fields
    required for the Wynwood House booking flow.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": _("Email address"), "autocomplete": "email"}
        ),
        label=_("Email address"),
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("First name")}),
        label=_("First name"),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Last name")}),
        label=_("Last name"),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("+1 555 000 0000")}),
        label=_("Phone number"),
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Country")}),
        label=_("Country"),
    )

    class Meta:
        model = User

        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "country",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Ensure the email address is not already registered."""
        email = self.cleaned_data.get("email", "").lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("An account with this email already exists."))

        return email

    def save(self, commit: bool = True) -> User:
        """Save the user, using email as the username."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.username = user.email
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone = self.cleaned_data.get("phone", "")
        user.country = self.cleaned_data.get("country", "")

        if commit:
            user.save()

        return user


class LoginForm(AuthenticationForm):
    """
    Login form using email address as the identifier.

    Inherits from Django's AuthenticationForm and overrides the username
    field label and widget to expect an email address.
    """

    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": _("Email address"), "autocomplete": "email"}
        ),
        label=_("Email address"),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": _("Password"), "autocomplete": "current-password"}
        ),
        label=_("Password"),
    )
