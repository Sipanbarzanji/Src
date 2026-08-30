from django.db import models
from django.contrib.auth.models import User
from workspace.models import create_and_update
class notifaction(create_and_update):
    class Meta:
        db_table="notifaction"
    update_at=None
    to_user=models.ForeignKey(User, related_name="notif_recieved", on_delete=models.CASCADE)
    by_user=models.ForeignKey(User, related_name="message_send", on_delete=models.CASCADE)
    message=models.TextField(max_length=150)
    is_read=models.BooleanField(default=False)
    
    
# Create your models here.
