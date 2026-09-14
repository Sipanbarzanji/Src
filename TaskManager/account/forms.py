from django import forms
from django.contrib.auth.models import User
class editprofileform(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),  
        required=False,          
        label="change password",
        help_text="If you don’t want to change it, leave it empty.",
    )
    class Meta:
        model=User
        fields=["username"]
        labels = {
            "username": "change username",
        }
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["password"].initial = "" 
        def save(self, commit=True):
            user = super().save(commit=False)
            password = self.cleaned_data.get("password")
            if password:
                user.set_password(password)
            if commit:
                user.save()
            return user

