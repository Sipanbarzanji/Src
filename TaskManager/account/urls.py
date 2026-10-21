from django.urls import path,include
from .views import signin,login,profile,editprofile,inbox,respond_notification
urlpatterns = [
    path('', login,name="login"),
    path('signin/',signin,name="signin"),
    path('profile/',profile,name='profile'),
    path("editprofile/",editprofile,name="editprofile"),
    path('workspacepage/', include('workspace.urls')),
    path("inbox/",inbox,name="inbox"),
    path("respond_notification/<int:pk>",respond_notification,name="respond_notification"),
]