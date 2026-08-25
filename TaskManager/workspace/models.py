from django.db import models
from django.contrib.auth.models import User
class create_and_update(models.Model):
    create_at=models.DateTimeField( auto_now_add=True)
    update_at=models.DateTimeField( auto_now=True)
class workspace(create_and_update):
    name=models.CharField( max_length=50)
    description=models.TextField()
    owner=models.ForeignKey(User,related_name="workspace", on_delete=models.CASCADE)
Role=[
    ("OW","owner"),
    ("AD","admin"),
    ("Mb","mebmer"),
]
class workspace_members(models.Model):
    user=models.ForeignKey(User,related_name="workspace_member", on_delete=models.CASCADE)
    worlspace=models.ForeignKey(workspace,related_name="workspace_member", on_delete=models.CASCADE)
    joined_at=models.DateTimeField(auto_now_add=True)
    role=models.CharField( max_length=2,choices=Role,default=("Mb","member"))
PROJECT_STATUS=[
    ("pn","planing"),
    ("ac","acting"),
    ("cp","complete")
]
class project(create_and_update):
    name=models.CharField( max_length=50)
    workspace=models.ForeignKey(workspace,related_name="workspace",on_delete=models.CASCADE)
    description=models.TextField()
    create_by=models.ForeignKey(User,related_name="projects_created", on_delete=models.CASCADE)
    status=models.CharField(max_length=2,choices=PROJECT_STATUS)
task_status=[
    ("td","todo"),
    ("ip","inprogres"),
    ("rw","rewie"),
    ("dn","done")
]
task_priority=[("lw","low"),
             ("md","medium"),
             ("hg","high"),
             ("nc","neccery")  
               ]
class tasks(create_and_update):
    title=models.CharField( max_length=50)
    description=models.TextField()
    project=models.ForeignKey(project,related_name="tasks", on_delete=models.CASCADE)
    assign=models.ForeignKey(User,related_name="tasks",on_delete=models.CASCADE)
    create_by=models.ForeignKey(User,related_name="tasks_created",on_delete=models.CASCADE)
    status=models.CharField( max_length=2,choices=task_status)
    priority=models.CharField( max_length=2,choices=task_priority)
    deadline=models.DateTimeField()
class comment(create_and_update):
    task=models.ForeignKey(tasks, related_name="comments", on_delete=models.CASCADE)
    user=models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content=models.TextField(max_length=150)
class files(create_and_update):
    task=models.ForeignKey(tasks, related_name="files", on_delete=models.CASCADE)
    file=models.FileField(upload_to="upload/")
    
label_name=[
    ("bg","bug"),
    ("fe","feature"),
    ("bk","backend"),
    ("fn","fronted"),
    ("ur","urgent")
    ("db","database")
]
class label(models.Model):
    name=models.CharField( max_length=2,choices=label_name)
    task_table=models.ManyToManyField(tasks, related_name="labels")
class logs(create_and_update):
    update_at=None
    user=models.ForeignKey(User, related_name="logs", on_delete=models.CASCADE)
    action=models.TextField()
class notifaction(create_and_update):
    update_at=None
    to_user=models.ForeignKey(User, related_name="notif_recieved", on_delete=models.CASCADE)
    by_user=models.ForeignKey(User, related_name="message_send", on_delete=models.CASCADE)
    message=models.TextField(max_length=150)
    is_read=models.BooleanField()
    
    
    