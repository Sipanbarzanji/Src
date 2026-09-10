from django.db import models
from django.contrib.auth.models import User
class create_and_update(models.Model):
    create_at=models.DateTimeField( auto_now_add=True)
    update_at=models.DateTimeField( auto_now=True)
    class Meta:
        abstract=True
class workspace(create_and_update):
    class Meta:
        db_table="workspace"
    name=models.CharField( max_length=50)
    description=models.TextField()
    owner=models.ForeignKey(User,related_name="workspaces_owner", on_delete=models.CASCADE)
Role=[
    ("OW","owner"),
    ("AD","admin"),
    ("Mb","mebmer"),
]
class workspace_members(models.Model):
    user=models.ForeignKey(User,related_name="workspace_member", on_delete=models.CASCADE)
    workspace=models.ForeignKey(workspace,related_name="workspace_member", on_delete=models.CASCADE)
    joined_at=models.DateTimeField(auto_now_add=True)
    role=models.CharField( max_length=2,choices=Role,default="Mb")
    class Meta:
        db_table="workspace_members"
        constraints=[
            models.UniqueConstraint(fields=["user","workspace"],
                                    name="unique_user_in_workspace")
        ]
PROJECT_STATUS=[
    ("pn","planing"),
    ("ac","acting"),
    ("cp","complete")
]
class project(create_and_update):
    class Meta:
        db_table="project"
    name=models.CharField( max_length=50)
    workspace=models.ForeignKey(workspace,related_name="projects",on_delete=models.CASCADE)
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
    class Meta:
        db_table="tasks"
    title=models.CharField( max_length=50)
    description=models.TextField()
    project=models.ForeignKey(project,related_name="tasks", on_delete=models.CASCADE)
    assign=models.ForeignKey(User,related_name="tasks",on_delete=models.CASCADE)
    create_by=models.ForeignKey(User,related_name="tasks_created",on_delete=models.CASCADE)
    status=models.CharField( max_length=2,choices=task_status)
    priority=models.CharField( max_length=2,choices=task_priority)
    deadline=models.DateTimeField()

class files(create_and_update):
    class Meta:
        db_table="files"
    task=models.ForeignKey(tasks, related_name="files", on_delete=models.CASCADE)
    file=models.FileField(upload_to="upload/")
    uploaded_by=models.ForeignKey(User,related_name="files_uploaded", on_delete=models.CASCADE)
    
label_name=[
    ("bg","bug"),
    ("fe","feature"),
    ("bk","backend"),
    ("fn","fronted"),
    ("ur","urgent"),
    ("db","database")
]
class label(models.Model):
    class Meta:
        db_table="label"
    name=models.CharField( max_length=2,choices=label_name)
    task_table=models.ManyToManyField(tasks, related_name="labels")
    def __str__(self):
        return self.name

    