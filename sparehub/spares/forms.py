from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Company, Customer

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Company, Customer

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'address']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.phone_number = self.cleaned_data.get('phone_number')
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                address=self.cleaned_data.get('address')
            )
        return user


class CompanyRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=100)
    registration_number = forms.CharField(max_length=50)
    company_address = forms.CharField(widget=forms.Textarea)
    registration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'company_name', 'registration_number', 'company_address', 'registration_date']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        if commit:
            user.save()
            Company.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name'),
                registration_number=self.cleaned_data.get('registration_number'),
                company_address=self.cleaned_data.get('company_address'),
                registration_date=self.cleaned_data.get('registration_date')
            )
        return user