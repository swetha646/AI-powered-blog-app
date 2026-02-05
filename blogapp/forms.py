from django.forms import ModelForm

from blogapp.models import *


class UserForm(ModelForm):
    class Meta:
        model = UserModel
        fields = '__all__'


class BlogForm(ModelForm):
    class Meta:
        model = BlogModel
        fields = '__all__'