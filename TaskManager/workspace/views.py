from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseBadRequest,Http404
from .models import workspace,workspace_members,project as projects,tasks,task_status,label
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import WorkspaceCreateForm,adduserform,addprojectform,editprojectform,addtaskform,commentform,replytform
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from comments.models import comment,reply


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
    wkspace=get_object_or_404(workspace,id=pk)
    wkmembers=workspace_members.objects.filter(workspace=wkspace)
    yourrole=workspace_members.objects.get(workspace=wkspace,user=request.user)
    if not yourrole:
        raise Http404("your not member of this workspace")
    return render(request,"workspace/workspacedetail.html",{"members":wkmembers,"workspace":wkspace,"yourrole":yourrole.role})
@login_required 
def projectpage(request):
    wkmem=request.user.workspace_member.all()
    projectss=[]
    for wk in wkmem:
        projectss.extend(wk.workspace.projects.all())
    return render(request,"workspace/projectpage.html",{"projects":projectss})
@login_required 
def projectdetail(request,pk):
    project=get_object_or_404(projects,id=pk)
    role=workspace_members.objects.get(user=request.user,workspace=project.workspace)
    if not role:
        raise Http404("your not member of this workspace")
    return render(request,"workspace/projectdetail.html",{"project":project,"role":role.role})
@login_required 

def taskpage(request):
    tasks_created=request.user.tasks_created.all()
    tasks_todo=request.user.tasks.all()
    return render(request,"workspace/taskpage.html",{"tasks_todo":tasks_todo,"tasks_created":tasks_created})
@login_required 
def taskdetail(request,pk):
    task=get_object_or_404(tasks,id=pk)
    role=workspace_members.objects.get(workspace=task.project.workspace,user=request.user)
    if not role:
        raise Http404("yor not member of this workspace")
    form=commentform()
    return render(request,"workspace/taskdetail.html",{"task":task,"role":role.role,"taskstatus":task_status,"form":form})
@login_required 
def adduser(request,pk):
    wkspace=get_object_or_404(workspace,id=pk)
    userrole=workspace_members.objects.get(workspace=wkspace,user=request.user)
    if not userrole:
        raise Http404("your not in this workspace")
    if userrole.role not in ["AD","OW"]:
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
    role=workspace_members.objects.get(workspace=wkspace,user=request.user)
    if not role:
        raise Http404("your not in this workspace")
    if role.role!="OW":
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
    role=workspace_members.objects.get(workspace=project.workspace,user=request.user)
    if not role:
        raise Http404("your not in this workspace")
    if role.role !="OW" and project.create_by != request.user :
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
    form=editprojectform(instance=project)
    return render(request,"workspace/editproject.html",{"form":form,"project":project,"role":role.role})
@login_required
@require_POST
def removeproject(request,pk):
    project=get_object_or_404(projects,id=pk)
    wkmem=workspace_members.objects.filter(workspace=project.workspace)
    role=wkmem.get(user=request.user)
    if not role:
        raise Http404("your not in this workspace")
    if role.role !="OW" and project.create_by != request.user :
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
@login_required
def addtask(request,pk):
    project=get_object_or_404(projects,id=pk)
    wkmem=workspace_members.objects.filter(workspace=project.workspace)
    role=wkmem.get(user=request.user)
    if not role:
        raise Http404("your not member of this workspace")
    if role.role not in ["OW",'AD']:
        raise PermissionDenied("you cant add task")
    if request.method=="POST":
        form=addtaskform(request.POST,workspace=project.workspace)
        if form.is_valid():
            new_task=form.save(commit=False)
            new_task.create_by=request.user
            new_task.assign=form.cleaned_data["assign"]
            new_task.project=project
            new_task.save()
            notifaction.objects.create(
                recipient=new_task.assign,
                message=f"in {project.workspace} user {request.user.first_name} {request.user.last_name} has create a task for you  ",
                notif_type="NT",
                target=new_task
            
          )
            
            for labell in form.cleaned_data["labels"] :
                label_obj=label.objects.create(name=labell)
                label_obj.task_table.add(new_task)
            return redirect("workspace:taskdetail",new_task.id)
    form=addtaskform(workspace=project.workspace)
    return render(request,"workspace/addtask.html",{"form":form})
@login_required
@require_POST
def deletetask(request,pk):
    task=get_object_or_404(tasks,id=pk)
    project_id=task.project.id
    role=workspace_members.objects.get(workspace=task.project.workspace,user=request.user).role
    if role !="OW" and task.project.create_by != request.user and task.create_by and request.user:
        raise PermissionDenied("toy cant delete this task")
    notifaction.objects.create(
                        recipient=task.assign,
                        message=f"{request.user.first_name} {request.user.last_name} has deleted {task.title} task",
                        notif_type="DT",
                        )
    task.delete()
    return redirect("workspace:projectdetail",project_id)
@login_required
@require_POST
def changetaskstatus(request,pk):
    task=get_object_or_404(tasks,id=pk)
    if task.create_by != request.user and task.assign != request.user:
        raise PermissionDenied("you cant change task status")
    status=request.POST.get("state")
    task.status=status
    task.save(update_fields=["status"])
    if task.create_by==request.user and task.create_by!=task.assign :
                            notifaction.objects.create(
                        recipient=task.assign,
                        message=f"{request.user.first_name} {request.user.last_name} has changed {task.title} status to {task.get_status_display()}",
                        notif_type="TS",  
                        target=task  
                        )
    elif(task.assign==request.user and task.create_by!=task.assign):
                                    notifaction.objects.create(
                        recipient=task.create_by,
                        message=f"{request.user.first_name} {request.user.last_name} has changed {task.title} status to {task.status}",
                        notif_type="TS",  
                        target=task  
                        )
    return redirect ("workspace:taskdetail",pk)
@login_required
@require_POST
def addcomment(request,pk):
    task=get_object_or_404(tasks,id=pk)
    if not workspace_members.objects.get(workspace=task.project.workspace,user=request.user):
        raise Http404("your not member of this workspace")
    form=commentform(request.POST)
    if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.task=task
            new_comment.save()
            for recipient in set([task.assign, task.create_by]):
               if recipient and recipient != request.user :
                 notifaction.objects.create(
                  recipient=recipient,
                     message=f"{request.user.first_name} {request.user.last_name} add a comment on {task.title} task",
                        notif_type="NC",
                     target=new_comment
                          )
            return redirect("workspace:taskdetail",pk)
    else:
        return redirect("workspace:taskdetail",pk)
@login_required
def addreply(request,pk):
    commentt=get_object_or_404(comment,id=pk)
    if not workspace_members.objects.get(workspace=commentt.task.project.workspace,user=request.user):
        raise Http404("your not member of this workspace")
    if request.method=="POST":
        form=replytform(request.POST)
        if form.is_valid():
                new_reply=form.save(commit=False)
                new_reply.user=request.user
                new_reply.comment_replyed=commentt
                new_reply.save()
                for recipient in set([commentt.task.assign, commentt.task.create_by,commentt.user]):
                    if recipient and recipient != request.user :
                        notifaction.objects.create(
                        recipient=recipient,
                            message=f"{request.user.first_name} {request.user.last_name} add a reply on {commentt.task.title} task",
                                notif_type="NC",
                            target=new_reply
                                )
                    return redirect("workspace:taskdetail",commentt.task.id)
    
    form=replytform()
    return render(request,"workspace/addreply.html",{"form":form,"comment":commentt})
def deletecomment(request,pk):
    coment=get_object_or_404(comment,id=pk,user=request.user)
    task_id=coment.task.id
    coment.delete()
    return redirect("workspace:taskdetail",task_id)  
def removereply(request,pk):
        replyy=get_object_or_404(reply,id=pk,user=request.user)
        task_id=replyy.comment_replyed.task.id
        replyy.delete()
        return redirect("workspace:taskdetail",task_id)