from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

import uuid

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email addree')

        if not username:
            raise ValueError('User must have an usernama')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user. is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    object = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    profile_picture = models.ImageField(blank=True, upload_to='photos/userprofile')
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100)
    country = models.CharField(blank=True, max_length=100)
    postcode = models.CharField(blank=True, max_length=20)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}' 

class Province(models.Model):
    name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class City(models.Model):
    KABUPATEN = 'Kabupaten'
    KOTA = 'Kota'

    CHOICES_TYPE = {
        (KABUPATEN, 'Kabupaten'),
        (KOTA, 'Kota'),
    }

    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=10, choices=CHOICES_TYPE, default=KOTA)
    post_code = models.CharField(max_length=20)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class District(models.Model):
    province = models.ForeignKey(Province, max_length=10, on_delete=models.CASCADE)
    city = models.ForeignKey(City,max_length=10, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Address(models.Model):
    """
        Address
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Account, verbose_name="User", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(verbose_name="Phone", max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    address_line_1 = models.CharField(verbose_name="Address Line 1", max_length=150)
    address_line_2 = models.CharField(verbose_name="Address Line 2", max_length=150)
    district = models.ForeignKey(District, verbose_name="District", on_delete=models.CASCADE, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)
    default = models.BooleanField(verbose_name="Default", default=False)
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Address"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}' 
