from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.RegistrationView.as_view(),
         name='registration'),
    path('pages/', include('pages.urls')),
]

handler403 = 'pages.views.csrf_failure'

handler404 = 'pages.views.page_not_found'

handler500 = 'pages.views.server_error'
