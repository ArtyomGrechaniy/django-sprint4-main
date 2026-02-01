from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

from users.forms import CustomUserCreationForm

urlpatterns = [
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('pages/', include('pages.urls')),
]

handler403 = 'core.views.csrf_failure'

handler404 = 'core.views.page_not_found'

handler500 = 'core.views.server_error'
