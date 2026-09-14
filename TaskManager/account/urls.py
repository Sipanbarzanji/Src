from django.urls import path
from .views import signin,login,profile,editprofile
urlpatterns = [
    path('', login,name="login"),
    path('signin/',signin,name="signin"),
    path('profile/',profile,name='profile'),
    path("editprofile/",editprofile,name="editprofile"),
]