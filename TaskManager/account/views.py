from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages

def signin(request):
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valis():
            user=form.save()
            login(request,user)
        else:
            messages.error(request, "خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.")
    else:
        form=UserCreationForm()
        return render(request,"account/signin.html",{"form":form})
def login(request):
    if request.method=="POST":
        form=AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
        else:
            form=AuthenticationForm()
            return render(request,"account/login.html",{"form":form})
            
# Create your views here.
