from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError('Please, provide an email address')
        if not password:
            raise ValueError('Please, provide a password')
        
        try:
            user = self.model(
                email=self.normalize_email(email),
                *args,
                **kwargs
            )
            user.set_password(password)
            user.save()
            return user
        except:
            raise ValueError('Please, try again.')
        
    def create_superuser(self, email, password = None, *args, **kwargs):
        try:
            user = self.create_user(
                email,
                password = password,
                is_admin=True,
                is_superuser=True,
                is_staff=True,
                *args,
                **kwargs
            )
            return user
        except:
            raise ValueError('An error occurred. Please,try again.')
            
        
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('hospital', 'Hospital'),
        ('donor', 'Donor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    username = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    groups = None
    user_permissions = None
    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()