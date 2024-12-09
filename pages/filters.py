from django import forms
from .models import Post

class PostFilterForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Post.client.all(), required=False)
    location = forms.ModelChoiceField(queryset=Post.location.all(), required=False)
