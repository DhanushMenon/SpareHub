# spares/views.py

from django.shortcuts import render

def index(request):
    return render(request, 'spares/index.html')

def browse(request):
    return render(request, 'spares/browse.html')

def home(request):
    return render(request, 'spares/home.html')

def signup(request):
    return render(request, 'spares/signup.html')

def login(request):
    return render(request, 'spares/login.html')