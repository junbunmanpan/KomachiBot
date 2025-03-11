from django import forms
from .models import TankaChat
from django.contrib.auth.forms import AuthenticationForm
import re

class TankaChatForm(forms.ModelForm):
    class Meta:
        model = TankaChat
        fields = ['line1', 'line2', 'line3', 'line4', 'line5']

class CustomLoginForm(AuthenticationForm):
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match("^[a-zA-Z0-9]+$", username):
            raise forms.ValidationError("ユーザー名は半角英数字のみ使用できます。")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not re.match("^[a-zA-Z0-9]+$", password):
            raise forms.ValidationError("パスワードは半角英数字のみ使用できます。")
        return password