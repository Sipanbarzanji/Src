from django import forms
from django.contrib.auth.models import User
from .models import project
class WorkspaceCreateForm(forms.Form):
    name = forms.CharField(max_length=50)
    description = forms.CharField(widget=forms.Textarea)
    invited_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Invite members",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["invited_users"].queryset = User.objects.all()
class adduserform(forms.Form):
    invited_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Invite members",
    )
    def __init__(self, *args, workspace=None, **kwargs):
        super().__init__(*args, **kwargs)
        if workspace is not None:
            self.fields["invited_users"].queryset = User.objects.exclude(
                workspace_member__workspace=workspace
            )
        else:
            self.fields["invited_users"].queryset = User.objects.none()

class addprojectform(forms.ModelForm):
    class Meta:
        model=project
        fields = ["name","description"]