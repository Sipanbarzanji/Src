from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login as Login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import editprofileform
from django.views.decorators.http import require_POST
from notifactions.models import notifaction as Notifaction
from workspace.models import workspace_members
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.db import transaction

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
            messages.error(request, "eror while regester try again")
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
            messages.error(request, "eror while login try again")
    else:
            form=AuthenticationForm()
    return render(request,"account/login.html",{"form":form})
@login_required
def profile(request):
    done_tasks=request.user.tasks.filter(status="dn").count
    tasks_todo=request.user.tasks.exclude(status="dn").count
    project_count=0
    new_massages=request.user.notifcations.filter(is_read=False).count
    for wk in request.user.workspace_member.all():
        project_count+=wk.workspace.projects.count()
    return render(request,"account/profile.html",{"user":request.user,"done_tasks":done_tasks,"tasks_todo":tasks_todo,"projects_count":project_count,"new_massages":new_massages})
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
@login_required
def inbox(request):
    qs = request.user.notifcations.all().order_by('-create_at')
    all_notifactions = list(qs)

    qs.filter(is_read=False).update(is_read=True)

    return render(request, "account/inbox.html", {
        "all_notifications": all_notifactions,
    })
@login_required
@require_POST
def respond_notification(request, pk):
    
    notification = get_object_or_404(
        Notifaction,
        pk=pk,
        
    )
    invitation=notification.target

    if notification.recipient==request.user:
        action = request.POST.get("action")
        if action not in ("accept", "reject"):
            return HttpResponseBadRequest("invalid action")


        with transaction.atomic():                  
            invitation = type(invitation).objects.select_for_update().get(pk=invitation.pk)

            if invitation.complete:                
                messages.warning(request, "this initation has answered before")
                return redirect("inbox")

            if action == "accept":
                invitation.status = "AC"
                invitation.complete = True
                invitation.save(update_fields=["status", "complete"])

                workspace_members.objects.get_or_create(
                    workspace=invitation.workspace, user=request.user
                )
                Notifaction.objects.create(
                    recipient=invitation.invited_by,
                    notif_type="IR",
                    target=invitation,
                    message=f"user {request.user.first_name} has accepted your request to join  {invitation.workspace.name}"
                )
                url = redirect("workspace:workspacedetial", pk=invitation.workspace.id)
            else:  # reject
                invitation.status = "RJ"
                invitation.complete = True
                invitation.save(update_fields=["status", "complete"])
                Notifaction.objects.create(
                    recipient=invitation.invited_by,
                    notif_type="IR",
                    target=invitation,
                    message=f"user {request.user.first_name} has rejected your request to join  {invitation.workspace.name}"
                )
                url = redirect("inbox")
        return url
    else:
            raise PermissionDenied("you dont have permission for this page")
