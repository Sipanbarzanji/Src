from django.urls import path
from .views import signin
urlpatterns = [
    path('', signin,name="signin"),
]