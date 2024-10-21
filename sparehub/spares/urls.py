from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from spares import views as spares_views

from django.urls import path
from . import views  # Import views from the current app
from .views import login_view, register_view, product_detail, CreateOrderView, PaymentVerificationView, payment_view, company_orders


from django.contrib.auth import views as auth_views
from django.conf.urls import include
from django.views.decorators.csrf import csrf_exempt

from social_django import views as social_views




app_name = 'spares'

urlpatterns = [
    path('', views.home, name='home'),  # Add this line
    path('login/', views.login_view, name='login_user'),  # Changed name to 'login_user'
    path('register/', views.register_view, name='register_user'),  # Changed name to 'register_user'),
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    path('complete-company-profile/', views.complete_company_profile, name='complete_company_profile'),
    path('edit-company-profile/', views.edit_company_profile, name='edit_company_profile'),
    path('logout/', views.logout_view, name='logout'),  # Add this line
    path('add-product/', views.add_product, name='add_product'),  # Add this line
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('toggle-availability/<int:product_id>/', views.toggle_availability, name='toggle_availability'),
    path('remove-product/<int:product_id>/', views.remove_product, name='remove_product'),
    path('browse/', views.browse_customer, name='browse_customer'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('cart/', views.view_cart, name='view_cart'),
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:product_id>/', views.update_cart_item, name='update_cart_item'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),


    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-company/<int:company_id>/', views.approve_company, name='approve_company'),
    path('revoke-approval/<int:company_id>/', views.revoke_approval, name='revoke_approval'),  # New URL pattern
    path('reject-company/<int:company_id>/', views.reject_company, name='reject_company'),

    # For category in home page
    path('category/<str:category>/', views.category_products, name='category_products'),  # New URL pattern


    path('product/<int:product_id>/', product_detail, name='product_detail'),

    path('payment/', payment_view, name='payment_view'),  # Ensure this line exists
    path('create-order/', CreateOrderView.as_view(), name='create_order'),  # Example for CreateOrderView
    path('verify-payment/', PaymentVerificationView.as_view(), name='verify-payment'),



    path('payment-success/', views.payment_success, name='payment_success'),
    path('company-orders/', company_orders, name='company_orders'),
    path('payment/success/', views.payment_success, name='payment_success'),



    path('oauth/', include('social_django.urls', namespace='social')),
    path('complete/<backend>/', csrf_exempt(social_views.complete), name='social:complete'),


]
