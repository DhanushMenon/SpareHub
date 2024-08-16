from django.contrib.auth.models import AbstractUser
from django.db import models


class UserType(models.Model):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.type_name

# Custom User Model
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    usertype = models.ForeignKey('UserType', on_delete=models.CASCADE, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.username

# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
