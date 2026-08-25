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
