from django.urls import path
from .views import workspacepage,workspacedetial,projectdetail,projectpage,taskpage,taskdetail
app_name = 'workspace'
urlpatterns = [
path("",workspacepage,name="workspacepage"),
path("<int:pk>/",workspacedetial,name="workspacedetial"),
path("projects",projectpage,name="projectpage"),
path("projects/<int:pk>/",projectdetail,name="projectdetail"),
path("tasks/",taskpage,name="taskpage"),
path("tasks/<int:pk>/",taskdetail,name='taskdetail')
]