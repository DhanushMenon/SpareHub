from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Company, Customer, Product, ProductImage

class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
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


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['company_name', 'company_address']  # Include only the fields you want to be editable
        # You can exclude the registration_number if you don't want it to be editable after registration


class ProductForm(forms.ModelForm):
    car_makes = forms.MultipleChoiceField(
        choices=[
            ('Any', 'Any'),
            ('TOYOTA', 'Toyota'),
            ('HONDA', 'Honda'),
            ('FORD', 'Ford'),
            ('BMW', 'BMW'),
            ('MERCEDES', 'Mercedes-Benz'),
            # Add more car makes as needed
        ],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock_quantity', 'warranty', 'availability', 'car_makes']


class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image')
    class Meta:
        model = ProductImage
        fields = ['image']

ProductImageFormSet = forms.inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=1)


class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=User.user_type.field.choices)
    car_makes = forms.MultipleChoiceField(
        choices=[
            ('Any', 'Any'),
            ('TOYOTA', 'Toyota'),
            ('HONDA', 'Honda'),
            ('FORD', 'Ford'),
            ('BMW', 'BMW'),
            ('MERCEDES', 'Mercedes-Benz'),
            # Add more car makes as needed
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    part_categories = forms.MultipleChoiceField(
        choices=[
            ('Any', 'Any'),
            ('BODY', 'Body'),
            ('ENGINE', 'Engine'),
            ('TRANSMISSION', 'Transmission'),
            ('AC', 'AC'),
            ('FUEL_SUPPLY', 'Fuel Supply'),
            ('BRAKE', 'Brake'),
            ('SUSPENSION', 'Suspension'),
            ('STEERING', 'Steering'),
            ('INTERIOR', 'Interior'),
            ('ELECTRONIC', 'Electronic Components'),
            ('EXHAUST', 'Exhaust System'),
            ('WHEELS', 'Wheels'),
            # Add more categories as needed
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    manufacturing_type = forms.ChoiceField(
        choices=[
            ('OEM', 'Original Equipment Manufacturer'),
            ('AFTERMARKET', 'Aftermarket'),
            ('REMANUFACTURED', 'Remanufactured'),
        ],
        required=False
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
            if user.user_type == 'COMPANY':
                Company.objects.create(
                    user=user,
                    car_makes=','.join(self.cleaned_data['car_makes']),
                    part_categories=','.join(self.cleaned_data['part_categories']),
                    manufacturing_type=self.cleaned_data['manufacturing_type']
                )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User







from django import forms

# Forgot Password Form
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)

# OTP Verification Form
class OTPVerificationForm(forms.Form):
    otp = forms.IntegerField(label='OTP', widget=forms.NumberInput(attrs={'min': 100000, 'max': 999999}))
    email = forms.EmailField(widget=forms.HiddenInput())  # This is hidden to store email for OTP verification

# Password Reset Form
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 8}), label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength': 8}), label='Confirm Password')

    # Validate that the two password fields match
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
