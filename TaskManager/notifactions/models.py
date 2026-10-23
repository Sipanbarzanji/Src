from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from workspace.models import workspace
from workspace.models import create_and_update
NOTIF_TYPE=[
    ("NT","new task"),
    ("CM","comment"),
    ("IN","invitation"),
    ("IR","invitation result"),
    ("CR","change role"),
]
class notifaction(create_and_update):
    class Meta:
        db_table="notifaction"
    recipient=models.ForeignKey(User, related_name="notifcations", on_delete=models.CASCADE)
    message=models.TextField(max_length=150)
    notif_type=models.CharField(max_length=3,choices=NOTIF_TYPE)
    is_read=models.BooleanField(default=False)
    content_type=models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,blank=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    target=GenericForeignKey("content_type","object_id")
class WorkspaceInvitation(create_and_update):
    workspace = models.ForeignKey(
        workspace,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workspace_invitations"
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations"
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ("PD", "Pending"),
            ("AC", "Accepted"),
            ("RJ", "Rejected"),
        ],
        default="pending"
    )
    complete=models.BooleanField(default=False)
    
# Create your models here.
