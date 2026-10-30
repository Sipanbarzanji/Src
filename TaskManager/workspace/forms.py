from django import forms
from django.contrib.auth.models import User
from .models import project,tasks
from datetime import date
from comments.models import comment,reply

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
class editprojectform(forms.ModelForm):
    class Meta:
        model=project
        fields=["name","description","status"]
class addtaskform(forms.ModelForm):
    class Meta:
        model=tasks
        fields=["title","description","priority","deadline"]
        widgets = {
            'deadline': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',     
            ),
        }
    assign= forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=True,
        widget=forms.Select,
        label="assign to",
    )
    label_name=[
    ("bg","bug"),
    ("fe","feature"),
    ("bk","backend"),
    ("fn","fronted"),
    ("ur","urgent"),
    ("db","database")
]
    labels = forms.MultipleChoiceField(
        choices=label_name,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='labels',
    )

    def __init__(self, *args, workspace=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].widget.attrs['min'] = date.today().strftime('%Y-%m-%dT%H:%M')
        self.fields['deadline'].input_formats = ['%Y-%m-%dT%H:%M']

        if workspace is not None:
            self.fields["assign"].queryset = User.objects.filter(
                workspace_member__workspace=workspace
            )
        else:
            self.fields["assign"].queryset = User.objects.none()

class commentform(forms.ModelForm):
    class Meta:
        model=comment
        fields=["content"]
class replytform(forms.ModelForm):
    class Meta:
        model=reply
        fields=["content"]