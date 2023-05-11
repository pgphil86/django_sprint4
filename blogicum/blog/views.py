from datetime import datetime

from django.shortcuts import get_object_or_404, render

from blog.models import Category, Post


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now(),
        ).select_related(
        'category',
        'author',
        )[:5]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.objects.filter(
            pub_date__lte=datetime.now(),
            is_published=True,
            category__is_published=True,
            pk=id,
        )
    )
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            slug=category_slug,
            is_published=True,
        )
    )
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now(),
    ).select_related(
        'category',
        'author',
        )
    context = {'post_list': post_list, 'category': category}
    return render(request, template, context)
