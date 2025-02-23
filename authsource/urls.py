from django.urls import path, include
from .views import *

app_name ='authsource'

urlpatterns = [
    path('', include([
        path('signup/', signup, name='signup'),
        path('activate/<str:uidb64>/<str:token>', activate, name='activate'),
        path('login/', signin, name='login'),
        path('logout/', signout, name='logout'),
        path('password_reset/', password_reset, name='reset_page'),
        path('password_reset/done/', resetPageDone, name='reset_page_done'),
        path('reset/<uidb64>/<token>', reset_password_confirm, name='password_reset_confirm'),
    ])),
    
]