from django.db import models
from workspace.models import create_and_update,tasks
from django.contrib.auth.models import User
class comment(create_and_update):
    class Meta:
        db_table="comment"
    task=models.ForeignKey(tasks, related_name="comments", on_delete=models.CASCADE)
    user=models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    content=models.TextField(max_length=300)
class reply(create_and_update):
    class Meta:
        db_table="reply"
    comment_replyed=models.ForeignKey(comment, related_name="replys", on_delete=models.CASCADE)
    user=models.ForeignKey(User,  related_name="replys", on_delete=models.CASCADE)
    content=models.TextField(max_length=300)
    
# Create your models here.
