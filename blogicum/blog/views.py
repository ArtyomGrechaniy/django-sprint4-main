from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  ListView, UpdateView)
from users.forms import ProfileUpdateForm
from datetime import timezone
from .constants import AMOUNT_OF_POSTS_PER_PAGE
from .forms import CommentCreateForm, PostCreateForm, PostDeleteForm
from .models import Category, Comment, Post
from .services import filter_posts_by_publication

User = get_user_model()


class BasePostListView(ListView):
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE

    def get_queryset(self):
        qs = filter_posts_by_publication()
        extra_filter = self.get_extra_filter()
        if extra_filter:
            qs = qs.filter(**extra_filter)
        return qs.order_by('-pub_date')

    def get_extra_filter(self):
        return None


class PostDetailRedirectMixin:
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class LoginRequiredMixin(UserPassesTestMixin):
    login_url = 'login'
    redirect_field_name = 'next'

    def test_func(self):
        return self.request.user.is_authenticated


class OnlyAuthorAccessMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class IndexView(BasePostListView, ListView):
    template_name = 'blog/index.html'


class CategoryPostView(BasePostListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE

    def get_extra_filter(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs['category_slug'], is_published=True
        )
        return {'category': self.category}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = AMOUNT_OF_POSTS_PER_PAGE

    def get_queryset(self):
        username = self.kwargs['username']
        self.profile = get_object_or_404(User, username=username)
        qs = Post.objects.filter(author=self.profile)
        if self.request.user == self.profile:
            return qs.select_related('category', 'location', 'author')\
                     .annotate(comment_count=Count('comments'))\
                     .order_by('-pub_date')

        return filter_posts_by_publication(qs).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(OnlyAuthorAccessMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def test_func(self):
        user = self.get_object()
        return user == self.request.user


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)

        if post.is_published and post.category.is_published:
            return post

        if (
            self.request.user.is_authenticated
            and post.author == self.request.user
        ):
            return post

        from django.http import Http404
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentCreateForm()
        context['comments'] = (
            self.object.comments
            .select_related('author')
            .order_by('created_at')
        )
        return context

    def post(self, request, *args, **kwargs):
        form = CommentCreateForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = self.object
            comment.save()
            return redirect('blog:post_detail', pk=self.object.pk)


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
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
    OnlyAuthorAccessMixin, PostDetailRedirectMixin, UpdateView
):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'pk'

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class PostDeleteView(OnlyAuthorAccessMixin, DeleteView):
    model = Post
    form_class = PostDeleteForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class CommentView(LoginRequiredMixin, PostDetailRedirectMixin, CreateView):
    model = Comment
    form_class = CommentCreateForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(
    OnlyAuthorAccessMixin, PostDetailRedirectMixin, UpdateView
):
    model = Comment
    form_class = CommentCreateForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_pk = self.kwargs['comment_id']
        comment = get_object_or_404(Comment, pk=comment_pk)
        return comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = self.get_form()
        return context

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(
    OnlyAuthorAccessMixin, PostDetailRedirectMixin, DeleteView
):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_pk = self.kwargs['pk']
        comment_pk = self.kwargs['comment_id']
        comment = get_object_or_404(
            Comment,
            pk=comment_pk,
            post__pk=post_pk
        )
        return comment
