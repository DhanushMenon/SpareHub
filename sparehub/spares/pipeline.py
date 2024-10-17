from django.core.exceptions import PermissionDenied
from spares.models import User

def ensure_customer_user(backend, user, *args, **kwargs):
    """
    Ensure that the logged-in user is a customer.
    Raise an error if the user is not a customer.
    """
    if user.user_type != 'CUSTOMER':
        raise PermissionDenied("Only customers can log in using Google.")


def set_role(backend, user, response, *args, **kwargs):
    """
    Ensure the user's role is set to 'CUSTOMER' after Google login.
    """
    # Ensure the user has the 'CUSTOMER' role
    if user.user_type != 'CUSTOMER':
        user.user_type = 'CUSTOMER'
        user.save()
