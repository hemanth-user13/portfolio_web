from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    
class UserDetails(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    ROLE_OPTIONS = (
        ("superadmin", 'Super Admin'),
        ("admin", 'Admin')
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)  
    role = models.CharField(max_length=20, choices=ROLE_OPTIONS, default='admin')
    created_at = models.DateTimeField(auto_now_add=True)
    salutation = models.CharField(max_length=10, default="")
    title = models.CharField(max_length=10, default="")
    # profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self): 
        return self.is_admin

class Salutations(models.Model):
    name=models.CharField(max_length=10,unique=True)

    def __str__(self):
        return f"{self.name}"
    
class Titles(models.Model):
    name=models.CharField(max_length=10,unique=True)
    def __str__(self):
        return f"{self.id} - {self.name}"
class FakeProductsData(models.Model):
    id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=1000,default="")
    price=models.CharField(max_length=200,default="")
    description = models.TextField(default="")
    category=models.CharField(max_length=200,default="")
    image=models.CharField(max_length=300,default="")
    rating=models.JSONField(default=dict)

    def __str__(self):
        return f"{self.title}"

class Products(models.Model):
    id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=1000)
    price=models.IntegerField()
    description=models.CharField(max_length=10000000)
    images=models.CharField(max_length=1000)
    created_at=models.CharField(max_length=1000)
    updated_at=models.CharField(max_length=1000)
    def __str__(self):
        return f"{self.title}"

class Movies(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name}"

class Partners(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=200,unique=True)
    address=models.CharField(max_length=1000, blank=True, null=True)
    zip_code=models.IntegerField()
    mobile_number=models.IntegerField()
    created_user_id=models.ForeignKey(
        UserDetails,
        on_delete=models.CASCADE, ## using the cascade if the users are deleted then user related partner will be also deleted 
        related_name="partners"
    )
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} {self.mobile_number}"