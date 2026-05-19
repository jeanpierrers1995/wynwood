from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import LoginForm, RegisterForm



class LoginView(DjangoLoginView):
    """
    Log in an existing user.

    Redirects to the next URL or home page on success.
    """
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class RegisterView(FormView):
    """
    Register a new user account.

    After successful registration the user is automatically logged in
    and redirected to the home page (or the next URL if provided).
    """
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("properties:home")

    def dispatch(self, request, *args, **kwargs):
        """Redirect already-authenticated users away from the registration page."""
        if request.user.is_authenticated:
            return redirect(self.success_url)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Save the user, log them in and show a welcome message."""
        user = form.save()

        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")

        messages.success(
            self.request,
            _("Welcome to Wynwood House, %(name)s!")
            % {"name": user.first_name or user.email},
        )

        next_url = self.request.GET.get("next", "")

        return redirect(next_url or self.success_url)

    def form_invalid(self, form):
        """Display an error message when the form has validation errors."""
        messages.error(self.request, _("Please correct the errors below."))

        return super().form_invalid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Display the authenticated user's profile and booking history.
    """
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        """Inject the user's bookings into the template context."""

        context = super().get_context_data(**kwargs)

        context["bookings"] = (
            self.request.user.bookings.select_related(
                "property", "property__destination"
            )
            .prefetch_related("property__images")
            .order_by("-created_at")
        )

        return context
