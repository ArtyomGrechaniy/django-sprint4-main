from django.urls import path, include

from . import views

app_name = 'blog'

post_patterns = [
    path('', views.PostDetailView.as_view(),
         name='post_detail'),
    path('edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('comment/', views.CommentView.as_view(),
         name='add_comment'),
    path('edit_comment/<int:comment_id>/', views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(),
         name='delete_comment'),
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/', include(post_patterns)),
    path('category/<slug:category_slug>/', views.CategoryPostView.as_view(),
         name='category_posts'),
    path('profile/<str:username>/', views.ProfileView.as_view(),
         name='profile'),
    path('profile/<str:username>/edit', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
]
