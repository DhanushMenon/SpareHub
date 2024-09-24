# spares/views.py

# spares/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer,User,Company, Product# Import your Customer model
from django.contrib.auth import authenticate, login,logout
from .forms import CompanyRegistrationForm, CustomerRegistrationForm, CompanyProfileForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required






@login_required
def add_product(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        image = request.FILES.get('image')
        stock_quantity = request.POST['stock_quantity']
        warranty_period = request.POST['warranty_period']
        is_available = request.POST.get('is_available') == 'True'
        
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            image=image,
            stock_quantity=stock_quantity,
            warranty_period=warranty_period,
            is_available=is_available,
            company=request.user
        )
        messages.success(request, 'Product added successfully.')
        return redirect('company_dashboard')
    return render(request, 'add_product.html')


@login_required
def company_dashboard(request):
    if not request.user.is_company:
        return redirect('login_company')
    products = Product.objects.all()
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





@login_required
def remove_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, company=request.user)
        product.delete()
        # messages.success(request, 'Product removed successfully.')
    return redirect('company_dashboard')