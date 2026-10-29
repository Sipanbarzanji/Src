from django.contrib import admin
from .models import   workspace,workspace_members,project,tasks,label
class projectinline(admin.TabularInline):
    model = project  
    fields = ["id", 
              "name",
    "description",
    "create_by",
    "status"
] 
    extra = 1 
@admin.register(workspace)
class workspaceadmin(admin.ModelAdmin):
    list_display = ['id',
    "name",
    "description",
    "owner"
    ]
    inlines = [projectinline]  

class taskinline(admin.TabularInline):
    model = tasks  
    fields = ["id", 
            "title",
            "description",
            "assign",
            "create_by",
            "status",
            "priority",
            "deadline",
] 
    extra = 1 
@admin.register(project)
class projectadmin(admin.ModelAdmin):
    list_display = ["id", 
              "name",
    "description",
    "create_by",
    "status"
    ]
    inlines = [taskinline]  # لیست Inline های خود را اینجا قرار دهید
class labelinline(admin.TabularInline):
    model = label.task_table.through
    fields = [
        "label"
] 
    extra = 1 
@admin.register(tasks)
class tasksadmin(admin.ModelAdmin):
    list_display = ["id", 
            "title",
            "description",
            "assign",
            "create_by",
            "status",
            "priority",
            "deadline",
    ]
    inlines = [labelinline]  # لیست Inline های خود را اینجا قرار دهید


