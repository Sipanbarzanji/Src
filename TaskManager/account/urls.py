from django.urls import path
from .views import signin,login,home
urlpatterns = [
    path('', login,name="login"),
    path('signin/',signin,name="signin"),
    path('home/',home,name='home'),
]