from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login as Login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import editprofileform
from django.contrib.auth import update_session_auth_hash

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            Login(request,user)
            return redirect(profile)  
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
            return redirect(profile)
        else:
            messages.error(request, "خطا در ورود. لطفاً دوباره تلاش کنید.")
    else:
            form=AuthenticationForm()
    return render(request,"account/login.html",{"form":form})
@login_required
def profile(request):
    done_tasks=request.user.tasks.filter(status="dn").count
    tasks_todo=request.user.tasks.exclude(status="dn").count
    project_count=0
    for wk in request.user.workspace_member.all():
        project_count+=wk.workspace.projects.count()
    return render(request,"account/profile.html",{"user":request.user,"done_tasks":done_tasks,"tasks_todo":tasks_todo,"projects_count":project_count})
@login_required
def editprofile(request):
    user = request.user
    form = editprofileform(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        if form.cleaned_data.get("password"):
            update_session_auth_hash(request, user)
        return redirect("profile")
    
    return render(request, "account/editprof.html", {"form": form})
# Create your views here.
