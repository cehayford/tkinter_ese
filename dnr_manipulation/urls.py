from django.urls import path
from .views import *

app_name = 'dnr_manipulation'

urlpatterns = [
    path('', home, name='home'),
    path('', donor_center_dashboard, name='donor_center'),
    path('donors/', donor_view.as_view(), name=''),
    path('add_donor/',add_donor, name='add_donor'),
    path('transfusion_center/', transfusion_center_dashboard, name='transfusion_center'),
    path('add_request/', blood_request, name='add_request'),
    # path('add_center/', add_center, name='add_center'),
    
]