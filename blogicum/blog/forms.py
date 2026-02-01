from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].widget = forms.DateInput(attrs={'type': 'date'})


class PostDeleteForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = []


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)