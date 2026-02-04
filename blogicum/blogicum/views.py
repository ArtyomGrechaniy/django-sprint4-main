from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from users.forms import UserCreationForm


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')