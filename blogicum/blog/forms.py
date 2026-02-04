from django import forms

from .models import Comment, Post


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['author']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )


class CommentCreateForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
