# spares/views.py

# spares/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer,User,Company, Product# Import your Customer model
from django.contrib.auth import authenticate, login,logout
from .forms import CompanyRegistrationForm, CustomerRegistrationForm, CompanyProfileForm, ProductForm, ProductImageFormSet
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Wishlist

# ... existing views ...

@login_required
def add_product(request):
    company = Company.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid():
            product = form.save(commit=False)
            product.company = company
            product.save()
            image_formset.instance = product
            image_formset.save()
            return redirect('company_dashboard')
    else:
        form = ProductForm()
        image_formset = ProductImageFormSet()
    return render(request, 'add_product.html', {'form': form, 'image_formset': image_formset})


@login_required
def company_dashboard(request):
    # Get the company associated with the logged-in user
    company = Company.objects.get(user=request.user)
    
    # Filter products to only show those associated with the logged-in company
    products = Product.objects.filter(company=company)
    
    return render(request, 'company_dashboard.html', {'products': products})

def browse_customer(request):
    products = Product.objects.filter(is_available=True)  # Fetch available products
    search_query = request.GET.get('search')
    category = request.GET.get('category')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category:
        products = products.filter(category__name=category)  # Adjust based on your category field

    return render(request, 'browse_customer.html', {'products': products})

def home(request):
    return render(request, 'home.html')





def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login_customer')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register_customer.html', {'form': form})



def login_customer(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_customer:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['is_customer'] = True
            messages.success(request, 'You have successfully logged in.')
            return redirect('browse_customer')
        else:
            messages.error(request, 'Invalid username or password, or not a customer account.')
    
    return render(request, 'login_customer.html')


def browse_customer(request):
    products = Product.objects.filter(is_available=True)  # Fetch available products
    search_query = request.GET.get('search')
    category = request.GET.get('category')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category:
        products = products.filter(category__name=category)  # Adjust based on your category field

    return render(request, 'browse_customer.html', {'products': products})

    
def register_company(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Company registration successful.')
            return redirect('company_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompanyRegistrationForm()
    return render(request, 'register_company.html', {'form': form})

def login_company(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_company:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['is_company'] = True
            messages.success(request, 'You have successfully logged in.')
            return redirect('company_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a company account')
    return render(request, 'login_company.html')

def company_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_company:
        return redirect('login_company')
    products = Product.objects.all()
    return render(request, 'company_dashboard.html', {'products': products})


def google_signup(request):
    # Placeholder for Google signup logic
    messages.success(request, "Google signup functionality is not yet implemented.")
    return redirect('register_customer')  # Redirect to the registration page or wherever appropriate

def browse_customer(request):
    products = Product.objects.filter(is_available=True)  # Fetch available products
    return render(request, 'browse_customer.html', {'products': products})


@require_POST
def logout_view(request):
    logout(request)
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'is_customer' in request.session:
        del request.session['is_customer']
    if 'is_company' in request.session:
        del request.session['is_company']
    messages.success(request, "You have been successfully logged out.")
    return redirect('login_customer')




@login_required
def edit_company_profile(request):
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('company_dashboard')
    else:
        form = CompanyProfileForm(instance=request.user.company)
    
    return render(request, 'edit_company_profile.html', {'form': form})



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user)
    
    if request.method == 'POST':
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock_quantity = request.POST['stock_quantity']
        product.warranty_period = request.POST['warranty_period']
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        # messages.success(request, 'Product updated successfully.')
        return redirect('company_dashboard')
    
    return render(request, 'edit_product.html', {'product': product})



@login_required
def toggle_product_availability(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, company=request.user)
        product.is_available = not product.is_available
        product.save()
        status = "available" if product.is_available else "unavailable"
        # messages.success(request, f'Product is now {status}.')
    return redirect('company_dashboard')





from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, company=request.user)
    product.delete()
    return redirect('company_dashboard')  # or wherever you want to redirect after deletion

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({'cart_count': cart.cartitem_set.count()})

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = cart.total_price()
    return render(request, 'view_cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1

    if cart_item.quantity > 0:
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return JsonResponse({'success': True})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.remove(product)
    return redirect('view_wishlist')

@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_products = wishlist.products.all()
    return render(request, 'view_wishlist.html', {'wishlist_products': wishlist_products})