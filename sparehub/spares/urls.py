from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('login/customer/', views.login_customer, name='login_customer'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/company/', views.login_company, name='login_company'),
    path('company_dashboard/', views.company_dashboard, name='company_dashboard'),
    path('google-signup/', views.google_signup, name='google_signup'),
    path('browse/', views.browse_customer, name='browse_customer'),
    path('logout/', views.logout_view, name='logout'), # Add this line
    path('add_product/', views.add_product, name='add_product'),
    path('logout/customer/', views.logout_view, name='logout_customer'),
    path('logout/company/', views.logout_view, name='logout_company'),
]