from django.contrib import admin
from .models import comment,reply
class replyinline(admin.TabularInline):
    model = reply  
    fields = ["content", 
              "user",
] 
    extra = 1 
@admin.register(comment)
class workspaceadmin(admin.ModelAdmin):
    list_display = ['content',
    "user",
    "task",
    ]
    inlines = [replyinline]  

# Register your models here.
