from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

USER_PROFILE_FIELDS = ('username', 'first_name', 'last_name')


class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = USER_PROFILE_FIELDS


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = USER_PROFILE_FIELDS
