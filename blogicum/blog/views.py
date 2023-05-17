from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post, User


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


class PostListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = 10

    def get_queryset(self):
        return get_posts_query().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now(),
        )


class CategoryListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/category.html'
    ordering = 'id'
    paginate_by = 10

    def get_queryset(self):
        return get_posts_query().filter(
            category__slug__exact=self.kwargs['category_slug'],
            is_published=True,
            category__is_published=True,
            pub_date__lt=timezone.now(),
        )

    def dispatch(self, request, *args, **kwargs):
        self.category = get_list_or_404(Category,
                                        slug=kwargs['category_slug'],
                                        is_published=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileForm

    def get_success_url(self):
        return reverse_lazy('blog:edit_profile')

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)


class ProfileListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = 10

    def get_queryset(self):
        return get_posts_query().filter(
            author__username__exact=self.kwargs['profile_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['profile_slug']
        )
        return context


class PostCreateView(CreateView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:create_post',
            kwargs={'username': self.request.user},
            )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(UpdateView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']},
            )

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Post,
            pk=self.kwargs['pk'],
            )
        return super().dispatch(
            request,
            *args,
            **kwargs,
            )


class PostDeleteView(DeleteView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:index')

    def delete_func(self):
        post = self.get_object()
        if self.request.user == post.author_pk:
            return True
        return False


class PostDetailView(DetailView, LoginRequiredMixin):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('post')
        )
        return context


class CommentCreateView(CreateView, LoginRequiredMixin):
    posts = None
    model = Comment
    template_name = 'blog/create.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(
            Post,
            pk=kwargs['post_pk'],
        )
        return super().dispatch(
            request,
            *args,
            **kwargs,
            )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.posts.pk},
            )


class CommentUpdateView(UpdateView, LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.comment.post.pk},
            )

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            author=request.user,
            )
        return super().dispatch(
            request,
            *args,
            **kwargs,
            )


class CommentDeleteView(DeleteView, LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.comment.post.pk},
            )

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(
            Comment,
            pk=kwargs['pk'],
            author=request.user,
            )
        return super().dispatch(
            request,
            *args,
            **kwargs,
            )
