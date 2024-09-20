# spares/views.py

# spares/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer,User,Company, Product# Import your Customer model
from django.contrib.auth import authenticate, login,logout
from .forms import CompanyRegistrationForm, CustomerRegistrationForm
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
    products = Product.objects.filter(is_available=True)
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
            return redirect('browse_customer')  # Make sure this URL name is defined in your urls.py
        else:
            messages.error(request, 'Invalid username or password, or not a customer account.')
    
    return render(request, 'login_customer.html')


def browse_customer(request):
    products = Product.objects.filter(is_available=True)
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
    products = Product.objects.filter(is_available=True)
    return render(request, 'browse_customer.html', {'products': products})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login_customer')