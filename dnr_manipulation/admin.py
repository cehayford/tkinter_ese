from django.contrib import admin
from .models import Donor, BloodGroup

admin.site.register(Donor)
admin.site.register(BloodGroup)