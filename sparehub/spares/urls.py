from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from spares import views as spares_views

from django.urls import path
from . import views  # Import views from the current app


from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),  # Home view
    path('register/customer/', views.register_customer, name='register_customer'),
    path('login/customer/', views.login_customer, name='login_customer'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/company/', views.login_company, name='login_company'),
    path('company_dashboard/', views.company_dashboard, name='company_dashboard'),
    path('google-signup/', views.google_signup, name='google_signup'),
    path('browse/', views.browse_customer, name='browse_customer'),
    path('logout/', views.logout_view, name='logout'),  # General logout view
    path('add_product/', views.add_product, name='add_product'),
    path('edit-profile/', views.edit_company_profile, name='edit_company_profile'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('toggle-product-availability/<int:product_id>/', views.toggle_product_availability, name='toggle_product_availability'),
    path('remove-product/<int:product_id>/', views.remove_product, name='remove_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('view-cart/', views.view_cart, name='view_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('view-wishlist/', views.view_wishlist, name='view_wishlist'),

    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('dashboard/remove_product/<int:product_id>/', views.remove_product, name='remove_product'),



    
]

