from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseBadRequest
from .models import workspace,workspace_members,project as projects,tasks
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import WorkspaceCreateForm,adduserform,addprojectform
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import PermissionDenied

from notifactions.models import WorkspaceInvitation,notifaction
@login_required 
def workspacepage(request):
    return render(request,"workspace/workspacepage.html",{"user":request.user})
@login_required 
def addworkspace(request):
    if request.method == "POST":
        form = WorkspaceCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                name = form.cleaned_data["name"]
                description = form.cleaned_data["description"]
                new_workspace = workspace.objects.create(
                    name=name,
                    description=description,
                    owner=request.user,
                )
                workspace_members.objects.create(
                    workspace=new_workspace,
                    user=request.user,
                    role="OW",
                )
                users = form.cleaned_data["invited_users"]

                for user in users:
                    if user == request.user:
                        continue
                    invitation = WorkspaceInvitation.objects.create(
                        workspace=new_workspace,
                        invited_by=request.user,
                        invited_user=user,
                    )
                    notifaction.objects.create(
                        recipient=user,
                        message=(
                            f"You were invited to join {name} "
                            f"by {request.user.username}"
                        ),
                        notif_type="IN",
                        target=invitation,
                    )
            return redirect("workspace:workspacepage")
    else:
        form = WorkspaceCreateForm()
    return render(request,"workspace/addworkspace.html",{"form": form},)
@login_required 
def workspacedetial(request,pk):
    wkspace=workspace.objects.get(id=pk)
    wkmembers=workspace_members.objects.filter(workspace=wkspace)
    yourrole=workspace_members.objects.get(workspace=wkspace,user=request.user).role
    return render(request,"workspace/workspacedetail.html",{"members":wkmembers,"workspace":wkspace,"yourrole":yourrole})
@login_required 
def projectpage(request):
    wkmem=request.user.workspace_member.all()
    projectss=[]
    for wk in wkmem:
        projectss.extend(wk.workspace.projects.all())
    return render(request,"workspace/projectpage.html",{"projects":projectss})
@login_required 

def projectdetail(request,pk):
    project=projects.objects.get(id=pk)
    return render(request,"workspace/projectdetail.html",{"project":project})
@login_required 

def taskpage(request):
    tasks=request.user.tasks.all()
    return render(request,"workspace/taskpage.html",{"tasks":tasks})
@login_required 

def taskdetail(request,pk):
    task=get_object_or_404(tasks,id=pk)
    return render(request,"workspace/taskdetail.html",{"task":task})
@login_required 
def adduser(request,pk):
    wkspace=get_object_or_404(workspace,id=pk)
    if request.method=="POST":
        form=adduserform(request.POST,workspace=wkspace)
        if form.is_valid():
                users = form.cleaned_data["invited_users"]
                for user in users:
                    invitation = WorkspaceInvitation.objects.create(
                        workspace=wkspace,
                        invited_by=request.user,
                        invited_user=user,
                    )
                    notifaction.objects.create(
                        recipient=user,
                        message=(
                            f"You were invited to join {wkspace.name} "
                            f"by {request.user.username}"
                        ),
                        notif_type="IN",
                        target=invitation,
                    )
                return redirect("workspace:workspacedetial",pk=wkspace.id)
    else:
        form = adduserform(workspace=wkspace)
        return render(request,"workspace/adduser.html",{"form":form})
@login_required

def changerole(request,wkmem):
    if wkmem.role!="AD":
        raise PermissionDenied("you dont have permition for change role")
    new_role=request.POST.get("change-role")
    if new_role not in ["AD","Mb"]:
        return HttpResponseBadRequest("invalid role")

    wkmem.role=new_role
    wkmem.save(update_fields=['role'])
    notifaction.objects.create(
        recipient=wkmem.user,
        message=f"your role changed to {wkmem.get_role_display()} by {request.user.first_name} {request.user.last_name}",
        notif_type="CR",
        
    )
    return redirect("workspace:workspacedetial",wkmem.workspace.id)
@login_required
def addproject(request,pk):
    
    wkspace=get_object_or_404(workspace,id=pk)
    role=get_object_or_404(workspace_members,workspace=wkspace,user=request.user)
    if not (role=="AD" or role=="OW"):
        raise PermissionDenied("you dont have permission for add project")
    if request.method=="POST":
        form=addprojectform(request.POST)
        if form.is_valid():
            new_project=form.save(commit=False)
            new_project.workspace=wkspace
            new_project.create_by=request.user
            new_project.save()
            wkmem=workspace_members.objects.filter(workspace=wkspace)
            for wk in wkmem:
                notifaction.objects.create(
                recipient=wk.user,
                message=f"{request.user} has create a new project name {new_project.name} in {wkspace.name} workspace ",
                notif_type="NP",
                )
            return redirect("workspace:projectdetail",new_project.id)
    else:
        form=addprojectform()
        return render(request,"workspace/addproject.html",{"form":form})