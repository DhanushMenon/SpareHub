# spares/views.py

# spares/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer,User,Company, Product# Import your Customer model
from django.contrib.auth import authenticate, login,logout
from .forms import CompanyRegistrationForm, CustomerRegistrationForm, CompanyProfileForm, ProductForm, ProductImageFormSet, CustomUserCreationForm, CustomAuthenticationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Wishlist
from django.urls import reverse
from django.views.decorators.cache import cache_control


# ... existing views ...
def home(request):
    return render(request, 'home.html')


# Admin_Dashboard

def admin_dashboard(request):
    if not request.user.is_staff:  # Ensure only staff/admin users can access
         return redirect('spares:home')

    # companies = Company.objects.all()  # Fetch all registered companies
    # return render(request, 'admin_dashboard.html', {'companies': companies})
    companies = Company.objects.all()  # Fetch all companies from the database
    return render(request, 'admin_dashboard.html', {'companies': companies}) 




def approve_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.is_approved = True
    company.save()
    return redirect('spares:admin_dashboard')  # Redirect to the admin dashboard or wherever you want

def revoke_approval(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    company.is_approved = False
    company.save()
    return redirect('spares:admin_dashboard')  # Redirect to the admin dashboard or wherever you want

def reject_company(request, company_id):
    company = Company.objects.get(id=company_id)
    company.is_approved = False  # Reject the company
    company.save()
    return redirect('spares:admin_dashboard')





def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.user_type == 'COMPANY':
                # Create a basic Company instance
                Company.objects.create(
                    user=user,
                    company_name=user.username,  # Use username as the company name
                    registration_number=f"REG-{user.id}",  # Generate a temporary registration number
                    company_address="Address to be updated"
                )
            # Instead of logging in the user, redirect to the login page
            #messages.success(request, 'Registration successful! Please log in.')
            return redirect('spares:login_user')  # Redirect to the login page
    else:
        form = CustomUserCreationForm()
    return render(request, 'register_user.html', {'form': form})

from .forms import CustomAuthenticationForm  # Ensure you have the correct import for your form

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # Check if the user is a superuser
                if user.is_superuser:
                    login(request, user)
                    return redirect('spares:admin_dashboard')  # Redirect to the admin dashboard

                # Check if the user is a company and if it's approved
                elif user.user_type == 'COMPANY':
                    if hasattr(user, 'company') and user.company.is_approved:
                        login(request, user)
                        return redirect('spares:company_dashboard')  # Redirect to company dashboard
                    else:
                        # Company not approved
                        return render(request, 'login_user.html', {
                            'form': form,
                            'error': 'Your company is not approved yet.'
                        })

                # For customers, redirect to the customer browsing page
                elif user.user_type == 'CUSTOMER':
                    login(request, user)
                    return redirect('spares:browse_customer')

            else:
                # Invalid credentials
                return render(request, 'login_user.html', {
                    'form': form,
                    'error': 'Invalid credentials.'
                })

    else:
        form = CustomAuthenticationForm()

    return render(request, 'login_user.html', {'form': form})


@login_required
def company_dashboard(request):
    # Fetch products for the logged-in company
    products = Product.objects.filter(company=request.user.company).order_by('-id')
    
    context = {
        'products': products,
    }
    return render(request, 'company_dashboard.html', context)



@login_required
def complete_company_profile(request):
    if request.user.user_type != 'COMPANY':
        return redirect('spares:home')
    
    company = Company.objects.get(user=request.user)
    
    if request.method == 'POST':
        company.company_name = request.POST.get('company_name')
        company.registration_number = request.POST.get('registration_number')
        company.company_address = request.POST.get('company_address')
        company.save()
        return redirect('spares:company_dashboard')
    
    return render(request, 'complete_company_profile.html', {'company': company})





@login_required
def edit_company_profile(request):
    if request.user.user_type != 'COMPANY':
        return redirect('spares:home')
    
    company = Company.objects.get(user=request.user)
    
    if request.method == 'POST':
        company.company_name = request.POST.get('company_name')
        company.registration_number = request.POST.get('registration_number')
        company.company_address = request.POST.get('company_address')
        company.save()
        return redirect('spares:company_dashboard')
    
    return render(request, 'edit_company_profile.html', {'company': company})





# Logout view with cache control
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)  # Log out the user
    return redirect('spares:home')  # Redirect to the home page after logout



@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=Product())
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.company = request.user.company
            product.save()
            formset.instance = product
            formset.save()
            return redirect('spares:company_dashboard')
    else:
        form = ProductForm()
        formset = ProductImageFormSet(instance=Product())
    
    return render(request, 'add_product.html', {
        'form': form,
        'formset': formset,
    })



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user.company)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('spares:company_dashboard')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    
    return render(request, 'edit_product.html', {
        'form': form,
        'formset': formset,
        'product': product
    })




@login_required
def toggle_availability(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user.company)
    product.availability = not product.availability  # Toggle the availability
    product.save()
    return redirect('spares:company_dashboard')


@login_required
def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user.company)
    if request.method == 'POST':
        product.delete()
    return redirect('spares:company_dashboard')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def browse_customer(request):
    products = Product.objects.filter(availability=True)
    
    # Handle search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    context = {
        'products': products,
    }
    return render(request, 'browse_customer.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({'success': True, 'message': 'Product added to cart successfully'})

@require_POST
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return JsonResponse({'success': True, 'message': 'Product added to wishlist successfully'})

from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def form_valid(self, form):
        login(self.request, form.get_user())
        if self.request.user.user_type == 'COMPANY':
            return redirect('company_dashboard')  # Redirect company users to their dashboard
        else:
            return redirect('browse_customer')  # Redirect customers to browse page

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def view_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    wishlist_products = wishlist.products.all() if wishlist else []
    return render(request, 'view_wishlist.html', {'wishlist_products': wishlist_products})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.cartitem_set.all() if cart else []  # Use cartitem_set to access related items
    return render(request, 'view_cart.html', {'cart_items': cart_items})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        wishlist.products.remove(product)
    return redirect('spares:view_wishlist')



@login_required
def remove_from_cart(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
    return redirect('spares:view_cart')


@login_required
def update_cart_item(request, product_id):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity <= 0:
            cart_item.delete()  # Remove item if quantity is 0 or less
        else:
            cart_item.quantity = new_quantity
            cart_item.clean()  # Validate the quantity against stock
            cart_item.save()

    return redirect('spares:view_cart')









# Forgot PAssword View

import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from .forms import ForgotPasswordForm, OTPVerificationForm, PasswordResetForm

# Simulate OTP storage (In production, use a model or cache)
otp_storage = {}

# Forgot Password View
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = random.randint(100000, 999999)
                otp_storage[email] = otp
                
                # Send OTP to the email
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is {otp}. Do not share this with anyone.',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'OTP has been sent to your email.')
                return redirect(reverse('verify_otp') + f'?email={email}')
            except User.DoesNotExist:
                form.add_error('email', 'Email address not found.')
    else:
        form = ForgotPasswordForm()

    # Update the template path
    return render(request, 'forgot_password/forgot_password.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            entered_otp = form.cleaned_data['otp']

            if email in otp_storage and otp_storage[email] == entered_otp:
                del otp_storage[email]
                messages.success(request, 'OTP verified! You can now reset your password.')
                return redirect(reverse('reset_password') + f'?email={email}')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        email = request.GET.get('email')
        form = OTPVerificationForm(initial={'email': email})

    return render(request, 'forgot_password/verify_otp.html', {'form': form})

def reset_password(request):
    email = request.GET.get('email')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset successfully! You can now log in.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password/reset_password.html', {'form': form})




# For category in homepage
def category_products(request, category):
    products = Product.objects.filter(category=category)  # Filter products by category
    return render(request, 'category_products.html', {'products': products, 'category': category})