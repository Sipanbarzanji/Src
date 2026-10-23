from django.urls import path,register_converter
from . import views 
from .models import workspace_members
from django.urls.converters import IntConverter
from django.shortcuts import get_object_or_404
class ModelConverter(IntConverter):
    model = None

    def to_python(self, value):
        return get_object_or_404(self.model, pk=super().to_python(value))

    def to_url(self, value):
        if isinstance(value, int):
            return str(value)
        return str(value.pk)


def model_converter():
    class Converter(ModelConverter):
        model = workspace_members
    return Converter
try:
    register_converter(model_converter(), 'workmem')
except ValueError:
    pass 
app_name = 'workspace'
urlpatterns = [
path("",views.workspacepage,name="workspacepage"),
path("<int:pk>/",views.workspacedetial,name="workspacedetial"),
path("projects",views.projectpage,name="projectpage"),
path("projects/<int:pk>/",views.projectdetail,name="projectdetail"),
path("tasks/",views.taskpage,name="taskpage"),
path("tasks/<int:pk>/",views.taskdetail,name='taskdetail'),
path("addworkspace/",views.addworkspace,name="addworkspace"),
path("adduser/<int:pk>/",views.adduser,name="adduser"),
path("changerole/<workmem:wkmem>",views.changerole,name="change_role"),
path("addproject/<int:pk>",views.addproject,name="addproject")
]