from django import forms
from django.contrib.auth.models import User
from .models import Profile, Team

class UserRegisterForm(forms.ModelForm):
    team_name = forms.CharField(max_length=100, help_text="Enter a new team name or join an existing one by typing its exact name.")
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data
