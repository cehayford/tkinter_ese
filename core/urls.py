from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authsource.urls')),
    path('', include('dnr_manipulation.urls')), 
]
