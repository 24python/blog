# by luffycity.com

from django import forms
from django.forms import widgets
from .models import UserInfo
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
class RegForm(forms.Form):

    user=forms.CharField(max_length=8,label="用户名",
                         widget=widgets.TextInput(attrs={"class":"form-control"})
                         )
    pwd=forms.CharField(min_length=4,label="密码",
                        widget=widgets.PasswordInput(attrs={"class":"form-control"}))
    repeat_pwd=forms.CharField(min_length=4,label="确认密码",
                         widget=widgets.PasswordInput(attrs={"class": "form-control"}))
    email=forms.EmailField(label="邮箱",
                         widget=widgets.EmailInput(attrs={"class": "form-control"})
    )


    def clean_user(self):
        val=self.cleaned_data.get("user")
        # val=self.cleaned_data.get("pwd")

        ret=UserInfo.objects.filter(username=val)
        if not ret:
            return val
        else:
            raise ValidationError("该用户已存在")

    def clean(self):
        if self.cleaned_data.get("pwd")==self.cleaned_data.get("repeat_pwd"):
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不一致！")
