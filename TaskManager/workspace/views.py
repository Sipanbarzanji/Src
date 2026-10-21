from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from .models import workspace,workspace_members,project as projects,tasks
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import WorkspaceCreateForm
from django.db.models import Q

from django.db import transaction

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
    return render(request,"workspace/workspacedetail.html",{"members":wkmembers,"workspace":wkspace})
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
# Create your views here.
