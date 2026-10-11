from django.urls import path
from .views import workspacepage,workspacedetial,projectdetail
app_name = 'workspace'
urlpatterns = [
path("",workspacepage,name="workspacepage"),
path("<int:pk>/",workspacedetial,name="workspacedetial"),
path("projects/<int:pk>/",projectdetail,name="projectdetail"),
]