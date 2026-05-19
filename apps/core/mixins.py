"""
Reusable CBV mixins for Wynwood House.

Centralises cross-cutting view behaviours that can be composed into
any view without duplicating code.
"""

from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.translation import gettext_lazy as _


class MessageMixin:
    """
    Add a flash success message after a successful form submission.

    Compatible with ``CreateView``, ``UpdateView`` and any view that
    implements ``form_valid``.

    Attributes:
        success_message: The message text to display. No message is
            added if this is empty.

    Example::

        class BookingCreateView(MessageMixin, CreateView):
            success_message = _("Your booking has been registered successfully!")
            ...
    """

    success_message: str = ""

    def form_valid(self, form):
        """Add the success message and delegate to the parent class.

        Args:
            form: The validated form.

        Returns:
            The HttpResponse from ``super().form_valid(form)``.
        """

        if self.success_message:
            messages.success(self.request, self.success_message)

        return super().form_valid(form)


class StaffRequiredMixin(LoginRequiredMixin):
    """
    Restrict access to users with ``is_staff=True``.

    Redirects to the login page if unauthenticated, or returns
    a permission-denied response if authenticated but not staff.
    """

    def dispatch(self, request, *args, **kwargs):
        """Verify authentication and staff permissions before dispatching."""

        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_staff:
            messages.error(
                request, _("You do not have permission to access this section.")
            )

            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin:
    """
    Restrict access to the owner of an object.

    Assumes the object has a field (default: ``guest``) that references
    the owning user. Customise by overriding ``get_owner()``.

    Attributes:
        owner_field: Name of the model field that holds the owner reference.
    """

    owner_field: str = "guest"

    def get_owner(self):
        """Return the user who owns the current object."""

        obj = self.get_object()

        return getattr(obj, self.owner_field, None)

    def dispatch(self, request, *args, **kwargs):
        """Verify the user is the owner before dispatching."""

        if not request.user.is_authenticated:
            return LoginRequiredMixin.handle_no_permission(self)

        owner = self.get_owner()

        if owner != request.user and not request.user.is_staff:
            messages.error(
                request, _("You do not have permission to perform this action.")
            )

            return LoginRequiredMixin.handle_no_permission(self)

        return super().dispatch(request, *args, **kwargs)
