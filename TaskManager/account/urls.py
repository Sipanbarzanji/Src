from django.urls import path
from .views import signin,login,profile
urlpatterns = [
    path('', login,name="login"),
    path('signin/',signin,name="signin"),
    path('profile/',profile,name='profile'),
]