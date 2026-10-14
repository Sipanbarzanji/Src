from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import workspace,workspace_members,project as projects,tasks
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
@login_required 
def workspacepage(request):
    
    return render(request,"workspace/workspacepage.html",{"user":request.user})
def workspacedetial(request,pk):
    wkspace=workspace.objects.get(id=pk)
    wkmembers=workspace_members.objects.filter(workspace=wkspace)
    return render(request,"workspace/workspacedetail.html",{"members":wkmembers,"workspace":wkspace})
def projectpage(request):
    wkmem=request.user.workspace_member.all()
    projectss=[]
    for wk in wkmem:
        projectss.extend(wk.workspace.projects.all())
    return render(request,"workspace/projectpage.html",{"projects":projectss})
def projectdetail(request,pk):
    project=projects.objects.get(id=pk)
    return render(request,"workspace/projectdetail.html",{"project":project})
def taskpage(request):
    tasks=request.user.tasks.all()
    return render(request,"workspace/taskpage.html",{"tasks":tasks})
def taskdetail(request,pk):
    task=get_object_or_404(tasks,id=pk)
    return render(request,"workspace/taskdetail.html",{"task":task})
# Create your views here.
