from datetime import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from users.forms import ProfileUpdateForm

from .constants import AMOUNT_OF_POSTS_PER_PAGE
from .forms import CommentCreateForm, PostCreateForm
from .mixins import AuthorRequiredMixin, CommentMixin, PostMixin
from .models import Category, Post

User = get_user_model()


class BasePostListView(ListView):
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE
    queryset = (
        Post.objects
        .published_with_comments()
        .with_related()
        .order_by('-pub_date')
    )


class IndexView(BasePostListView, ListView):
    template_name = 'blog/index.html'


class CategoryPostView(BasePostListView):
    model = Post
    template_name = 'blog/category.html'

    def get_category(self):
        if not hasattr(self, 'category'):
            self.category = get_object_or_404(
                Category,
                slug=self.kwargs['category_slug'],
                is_published=True
            )
        return self.category

    def get_queryset(self):
        return (
            Post.objects
            .published_with_comments()
            .with_related()
            .filter(category=self.get_category())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE

    def get_author(self):
        if not hasattr(self, 'author'):
            self.author = get_object_or_404(
                User,
                username=self.kwargs['username']
            )
        return self.author

    def get_queryset(self):
        author = self.get_author()
        qs = (
            Post.objects
            .with_related()
            .filter(author=author)
            .with_comment_count()
        )

        if self.request.user != author:
            qs = qs.published()

        return qs.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.object.username}
        )


class PostDetailView(ListView):
    template_name = 'blog/detail.html'
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        if post.author == self.request.user:
            return get_object_or_404(Post, pk=self.kwargs['post_id'])

        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True,
            category__is_published=True,
        )

    def get_queryset(self):
        return (
            self.get_object().comments
            .select_related('author')
            .order_by('created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm()
        context['post'] = self.get_object()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if not form.instance.pub_date:
            form.instance.pub_date = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentView(CommentMixin, CreateView):
    form_class = CommentCreateForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(AuthorRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentCreateForm


class CommentDeleteView(AuthorRequiredMixin, CommentMixin, DeleteView):
    pass
