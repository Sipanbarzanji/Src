from django.db import models
from workspace.models import create_and_update
from django.contrib.auth.models import User
class logs(create_and_update):
    class Meta:
        db_table="logs"
    update_at=None
    user=models.ForeignKey(User, related_name="logs", on_delete=models.CASCADE)
    action=models.TextField()

# Create your models here.
