from blog.constans import PAGINATOR
from blog.forms import CommentForm, PostForm, ProfileForm
from blog.models import Category, Comment, Post, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)


def get_posts_query():
    return Post.objects.select_related(
        'category', 'location', 'author').only(
        'id',
        'title',
        'pub_date',
        'location',
        'location__name',
        'author__username',
        'category__slug',
        'category__title',
        'text',
    )


class PostCommentDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            self.model,
            pk=self.kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(
            request,
            *args,
            **kwargs)


class PostListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = PAGINATOR

    def get_queryset(self):
        return get_posts_query().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now(),
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))


class CategoryListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/category.html'
    ordering = 'id'
    paginate_by = PAGINATOR

    def get_queryset(self):
        slug_url_kwarg = self.kwargs['category_slug']
        self.category = get_object_or_404(
            Category,
            slug=slug_url_kwarg,
            is_published=True)
        return get_posts_query().filter(
            category__slug__exact=self.category.slug,
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now(),
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = reverse_lazy('blog:edit_profile')

    def get_object(self):
        return self.request.user


class ProfileListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = PAGINATOR

    def get_queryset(self):
        username = self.kwargs['username']
        return get_posts_query().filter(
            author__username__exact=username
        ).order_by('-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        username = self.kwargs['username']
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(
            username=username
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostCommentDispatchMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(LoginRequiredMixin, PostCommentDispatchMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:index')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (self.object.comments.select_related('post'))
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/create.html'
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, PostCommentDispatchMixin,
                        UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(LoginRequiredMixin, PostCommentDispatchMixin,
                        DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.kwargs['pk']})
