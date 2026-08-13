from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login as Login
from django.contrib import messages
from django.http import HttpResponse

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            Login(request,user)
            return redirect("home")  
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
            Login(request,user)
            return redirect("home")
        else:
            messages.error(request, "خطا در ورود. لطفاً دوباره تلاش کنید.")
    else:
            form=AuthenticationForm()
    return render(request,"account/login.html",{"form":form})
def home(request):
    return HttpResponse("HOME")            
# Create your views here.
