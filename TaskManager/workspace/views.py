from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseBadRequest,Http404
from .models import workspace,workspace_members,project as projects,tasks
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import WorkspaceCreateForm,adduserform,addprojectform,editprojectform
from django.db.models import Q
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST


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
    try:
        role=workspace_members.objects.get(user=request.user,workspace=project.workspace).role
    except:
        raise Http404("ypur not member of this workspace")
    return render(request,"workspace/projectdetail.html",{"project":project,"role":role})
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
    try:
        userrole=workspace_members.objects.get(workspace=wkspace,user=request.user).role
    except:
        raise Http404("tour not in this workspace")
    if userrole not in ["AD","OW"]:
        raise PermissionError("you dont have permission for add user")
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
    form = adduserform(workspace=wkspace)
    return render(request,"workspace/adduser.html",{"form":form})
@login_required
@require_POST
def changerole(request,wkmem):
    user_role=workspace_members.objects.get(workspace=wkmem.workspace,user=request.user).role
    if user_role not in ["AD","OW"]:
        raise PermissionDenied("you dont have permition for change role")
    new_role=request.POST.get("action")
    if new_role not in ["AD","Mb","remove"]:
        return HttpResponseBadRequest("invalid role")
    pk=wkmem.workspace.id
    if new_role in ["AD","Mb"]:
        wkmem.role=new_role
        wkmem.save(update_fields=['role'])
        notifaction.objects.create(
            recipient=wkmem.user,
            message=f"your role changed to {wkmem.get_role_display()} by {request.user.first_name} {request.user.last_name}",
            notif_type="CR",
            
        )
    else:#remove user
        if user_role != "OW":
            raise PermissionDenied("you dont have permition for remove users")
        notifaction.objects.create(
            recipient=wkmem.user,
            message=f"your was removed from {wkmem.workspace.name} by {request.user.first_name} {request.user.last_name}",
            notif_type="RW",
            
        )
        wkmem.delete()
    return redirect("workspace:workspacedetial",pk)
@login_required
def addproject(request,pk):
    
    wkspace=get_object_or_404(workspace,id=pk)
    role=get_object_or_404(workspace_members,workspace=wkspace,user=request.user)
    if role.role not in ["AD","OW"]:
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
    
    form=addprojectform()
    return render(request,"workspace/addproject.html",{"form":form})
@require_POST
@login_required
def removeworkspace(request,pk):
    wkspace=get_object_or_404(workspace,id=pk)
    try:
        role=workspace_members.objects.get(workspace=wkspace,user=request.user).role
    except:
        raise Http404("your not in this workspace")
    if role!="OW":
        raise PermissionDenied("you dont have permisstion for remove this workspace")
    wkmem=workspace_members.objects.filter(workspace=wkspace).exclude(user=request.user)
    for user in wkmem:
            notifaction.objects.create(
            recipient=user.user,
            message=f"workspace {wkspace.name} has removed by {request.user.first_name} {request.user.last_name}",
            notif_type="WR",
            
        )
    wkspace.delete()
    return redirect("workspace:workspacepage")
@login_required
def editproject(request,pk):
    project=get_object_or_404(projects,id=pk)
    try:
        role=workspace_members.objects.get(workspace=project.workspace,user=request.user).role
    except:
        raise Http404("your not in this workspace")
    if role !="OW" and project.create_by != request.user :
        raise PermissionDenied("you dont have permission for delete this project")

    if request.method=="POST":
        form=editprojectform(request.POST,instance=project)
        if form.is_valid():
            form.save()
            wkmem=workspace_members.objects.filter(workspace=project.workspace).exclude(user=request.user)
            for mem in wkmem:
                for field in form.changed_data:
                    new = form.cleaned_data.get(field)
                    if field == "status":
                        if new=="pn":
                            new= "planing"
                        elif new=="ac":
                            new="acting"
                        else :
                            new="complete"
                    else:
                        new = form.cleaned_data.get(field)
                    notifaction.objects.create(
                        recipient=mem.user,
                        message=f"{request.user.first_name} {request.user.last_name} has changed {project.name} {field} to {new}",
                        notif_type="WR",    
                        )

        return redirect("workspace:projectdetail",pk)
    role=workspace_members.objects.get(workspace=project.workspace,user=request.user).role
    form=editprojectform(instance=project)
    return render(request,"workspace/editproject.html",{"form":form,"project":project,"role":role})
@login_required
@require_POST
def removeproject(request,pk):
    project=get_object_or_404(projects,id=pk)
    try:
        wkmem=workspace_members.objects.filter(workspace=project.workspace)
        role=wkmem.get(user=request.user).role
    except:
        raise Http404("your not in this workspace")
    if role !="OW" and project.create_by != request.user :
        raise PermissionDenied("you dont have permission for delete this project")
    for mem in wkmem:
            if mem.user==request.user:
                continue
            notifaction.objects.create(
            recipient=mem.user,
            message=f"{request.user.first_name} {request.user.last_name} has removed {project.name} project",
            notif_type="RP",
        )
    project.delete()
    return redirect("workspace:projectpage")