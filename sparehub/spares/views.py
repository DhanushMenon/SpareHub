# spares/views.py

# spares/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer,User,Company, Product, Order, OrderItem # Import your Customer model
from django.contrib.auth import authenticate, login,logout
from .forms import CompanyRegistrationForm, CustomerRegistrationForm, CompanyProfileForm, ProductForm, ProductImageFormSet, CustomUserCreationForm, CustomAuthenticationForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Wishlist, Order
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.cache import cache_control
import json
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Cart, CartItem
from django.db import transaction  # Add this import
from django.db import transaction
from django.contrib import messages
import logging
from django.contrib.auth import get_user_model






logger = logging.getLogger(__name__)

# ... existing views ...
def home(request):
    return render(request, 'home.html')


# Admin_Dashboard

def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('spares:home')
    
    companies = Company.objects.all().order_by('-id')
    return render(request, 'admin_dashboard.html', {'companies': companies})




def approve_company(request, company_id):
    if not request.user.is_staff:
        return redirect('spares:home')
    company = get_object_or_404(Company, id=company_id)
    company.is_approved = True
    company.save()
    messages.success(request, f'{company.company_name} has been approved.')
    return redirect('spares:admin_dashboard')

def revoke_approval(request, company_id):
    if not request.user.is_staff:
        return redirect('spares:home')
    company = get_object_or_404(Company, id=company_id)
    company.is_approved = False
    company.save()
    messages.success(request, f'Approval for {company.company_name} has been revoked.')
    return redirect('spares:admin_dashboard')

def reject_company(request, company_id):
    company = Company.objects.get(id=company_id)
    company.is_approved = False  # Reject the company
    company.save()
    return redirect('spares:admin_dashboard')




def register_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')  # Get the user type from the form
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = user_type  # Set user type based on the form input
            user.save()

            if user_type == 'COMPANY':
                Company.objects.create(
                    user=user,
                    company_name=form.cleaned_data.get('company_name', user.username),
                    registration_number=form.cleaned_data.get('registration_number', f"REG-{user.id}"),
                    company_address=form.cleaned_data.get('company_address', "Address to be updated"),
                    is_approved=False
                )
              #  messages.success(request, 'Registration successful! Please wait for admin approval before logging in.')
            elif user_type == 'CUSTOMER':
             messages.success(request, 'Registration successful! You can now log in.')

            return redirect('spares:login_user')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register_user.html', {'form': form})

from .forms import CustomAuthenticationForm  # Ensure you have the correct import for your form


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                login(request, user)
                return redirect('spares:admin_dashboard')
            if user.user_type == 'COMPANY':
                if not user.company.is_approved:
                    messages.error(request, 'Your company registration is pending approval.')
                    login(request, user)
                    return render(request, 'login_user.html')
                return redirect('spares:company_dashboard')
            if user.user_type == 'CUSTOMER':
                login(request, user)
                return redirect('spares:browse_customer')
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Incorrect password. Please try again.')
            else:
                messages.error(request, 'Username not found. Please check your username.')

    return render(request, 'login_user.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)  # Fixed whitespace
@login_required
def company_dashboard(request):
    products = Product.objects.filter(company=request.user.company).order_by('-id')
    orders = Order.objects.filter(items__product__in=products).distinct()
    
    context = {
        'products': products,
        'orders': orders,
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
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()  # Save the images
            messages.success(request, 'Product updated successfully!')
            return redirect('spares:company_dashboard')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'formset': formset})



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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def browse_customer(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    car_make_filter = request.GET.get('car_make', '')

    products = Product.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category=category_filter)

    if car_make_filter and car_make_filter != "ANY":
        products = products.filter(car_makes=car_make_filter)  # Assuming you have a car_make field in your Product model

    # Add stock information to each product
    for product in products:
        product.in_stock = product.stock_quantity > 0

    return render(request, 'browse_customer.html', {'products': products})

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        return JsonResponse({'success': False, 'message': 'Product is already in the cart.'})
    
    cart_item.quantity += 1
    cart_item.save()
    
    return JsonResponse({'success': True, 'message': 'Product added to cart successfully'})

@require_POST
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        return JsonResponse({'success': False, 'message': 'Product is already in the wishlist.'})
    
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
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_items = cart.cartitem_set.all().select_related('product')
    
    # Update cart items based on current stock
    for item in cart_items:
        if item.quantity > item.product.stock_quantity:
            item.quantity = item.product.stock_quantity
            item.save()
    
    total_amount = sum(item.subtotal() for item in cart_items)
    
    return render(request, 'view_cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.filter(user=request.user).first()
    if wishlist:
        wishlist.products.remove(product)
    return redirect('spares:view_wishlist')



@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
            cart_item.delete()
            return JsonResponse({'success': True, 'message': 'Item removed successfully'})
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



@login_required
def update_cart_item(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                message = 'Cart updated successfully'
            else:
                cart_item.delete()
                message = 'Item removed from cart'
            
            return JsonResponse({'success': True, 'message': message})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})








# Forgot PAssword View

import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
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
                return redirect(reverse('spares:verify_otp') + f'?email={email}&sent_otp=1')  # Add a query parameter to indicate success
            except User.DoesNotExist:
                form.add_error('email', 'Email address not found.')
    else:
        form = ForgotPasswordForm()

    return render(request, 'forgot_password/forgot_password.html', {'form': form})

# Verify OTP
def verify_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            entered_otp = form.cleaned_data['otp']

            if email in otp_storage and otp_storage[email] == entered_otp:
                del otp_storage[email]
                return redirect(reverse('spares:reset_password') + f'?email={email}&verified_otp=1')  # Success indicator
            else:
                form.add_error('otp', 'Invalid OTP.')  # Show error in the form
    else:
        email = request.GET.get('email')
        form = OTPVerificationForm(initial={'email': email})

    return render(request, 'forgot_password/verify_otp.html', {'form': form})

# Reset Password
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
                return redirect('spares:login_user')  # Redirect after successful password reset
            except User.DoesNotExist:
                form.add_error(None, 'User not found.')
    else:
        form = PasswordResetForm()

    return render(request, 'forgot_password/reset_password.html', {'form': form})



# For category in homepage
def category_products(request, category):
    products = Product.objects.filter(category=category)  # Filter products by category
    return render(request, 'category_products.html', {'products': products, 'category': category})



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.in_stock = product.stock_quantity > 0
    return render(request, 'product_detail.html', {
        'product': product
    })




# Payment Gateway
# views.py
# views.py

from django.shortcuts import render, get_object_or_404
from .models import Cart, CartItem

@login_required
def payment_view(request):
    # Get or create a cart for the user
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get all cart items
    cart_items = cart.cartitem_set.all()
    
    # Calculate total amount (no GST or shipping charges)
    total_amount = sum(item.subtotal() for item in cart_items)  # Total in INR
    total_bill = total_amount  # Total bill is now just the total amount

    return render(request, 'payment.html', {
        'total_amount': total_amount,
        'total_amount_in_paise': total_amount * 100  # Convert to paise
    })

class CreateOrderView(View):
    def post(self, request):
        try:
            # Attempt to decode the JSON body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Check if the required fields are present
        amount = data.get('amount')
        if amount is None:
            return JsonResponse({'error': 'Amount is required'}, status=400)

        # Create a Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Define the order details
        order_data = {
            "amount": amount,  # Amount in paise
            "currency": data.get('currency', 'INR'),  # Default to INR
            "receipt": "receipt#1",
            "payment_capture": 1  # Auto capture payment
        }

        # Create an order
        order = client.order.create(data=order_data)
        return JsonResponse(order)

class PaymentVerificationView(View):
    def post(self, request):
        # Get the payment details from the request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            # Payment is verified
            return JsonResponse({'status': 'success'})
        except Exception as e:
            # Payment verification failed
            return JsonResponse({'status': 'failed', 'error': str(e)})


@login_required
@transaction.atomic
def payment_success(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        # Verify the payment signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except:
            # If verification fails, redirect to a failure page
            return render(request, 'payment_failure.html')

        # Payment verified, now process the order
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        
        # Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create the order
        order = Order.objects.create(user=request.user, total_amount=total_amount)
        
        for cart_item in cart_items:
            product = cart_item.product
            if product.stock_quantity >= cart_item.quantity:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=product.price
                )
                product.stock_quantity -= cart_item.quantity
                product.save()
            else:
                # If stock is insufficient, rollback the transaction
                transaction.set_rollback(True)
                return render(request, 'payment_failure.html', {'message': f"Insufficient stock for {product.name}"})
        
        # Clear the cart
        cart.cartitem_set.all().delete()
        
        return render(request, 'payment_success.html', {'order': order})
    else:
        return redirect('spares:view_cart')

from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import Order


def company_orders(request):
    # Assuming the user is a company user and has a related Company model
    orders = Order.objects.filter(product__company=request.user.company).order_by('-order_date')
    return render(request, 'company_orders.html', {'orders': orders})











