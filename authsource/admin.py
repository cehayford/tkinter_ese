from .models import CustomUser
from django.contrib.admin import *

site.register(CustomUser)

class CustomUserAdmin(ModelAdmin):
    pass