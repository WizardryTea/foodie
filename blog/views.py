from datetime import datetime

from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q # Добавляем Q для сложных фильтров
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, User, Comment

from django.http import JsonResponse
from django.db import connection

NUMBER_OF_PAGINATOR_PAGES = 2

def get_posts(**kwargs):
    """Отфильтрованное получение постов"""
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).annotate(comment_count=Count('comments')
               ).filter(**kwargs).order_by('-pub_date')


def get_paginator(request, queryset, number_of_pages=NUMBER_OF_PAGINATOR_PAGES):
    """Представление queryset в виде пагинатора,
       по N-шт на странице"""
    paginator = Paginator(queryset, number_of_pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def get_post_count():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM blog_post WHERE is_published = TRUE")
        row = cursor.fetchone()
    return row[0]  # Возвращаем количество постов
    
def index(request):
    """Главная страница / Лента публикаций"""

    post_count = get_post_count()  # Получаем количество постов
    posts = Post.objects.all()  # основной запрос на получение постов

    dishes_html = get_dishes_html()  # Получаем HTML блюда

    location = request.GET.get('location')
    author = request.GET.get('author')

    # Базовый запрос на получение постов
    posts = get_posts(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now()
    )

    # Добавляем фильтры
    if location:
        posts = posts.filter(location__name__icontains=location)
    if author:
        posts = posts.filter(author__username__icontains=author)

    page_obj = get_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'location': location,
        'author': author,
        'posts': posts,
        'post_count': post_count,
        'dishes_html': dishes_html,  # Передаем в контекст
    }
    return render(request, 'blog/index.html', context)

def category_posts(request, category_slug):
    """Отображение публикаций в категории"""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    posts = get_posts(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(),
        category=category)
    page_obj = get_paginator(request, posts)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, 'blog/post_list.html', context)


def post_detail(request, post_id):
    """Отображение полного описания выбранной публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(
            Post,
            id=post_id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now())
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related(
        'author').filter(post=post)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    """Создание публикации"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    """Редактирование публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Удаление публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment,
               'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


def profile(request, username):
    """Отображение страницы пользователя"""
    profile = get_object_or_404(
        User,
        username=username)
    posts = get_posts(author=profile)
    if request.user != profile:
        posts = get_posts(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now(),
            author=profile)
    page_obj = get_paginator(request, posts)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Редактирование страницы пользователя"""
    profile = get_object_or_404(
        User,
        username=request.user)
    form = UserForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/user.html', context)


def post_list(request):
    form = PostFilterForm(request.GET) #Создаем форму из GET запроса

    queryset = Post.objects.all()

    if form.is_valid():
        location = form.cleaned_data.get('location')
        author = form.cleaned_data.get('author')

        if location:
            queryset = queryset.filter(location=location)
        if author:
            queryset = queryset.filter(author__icontains=author)

    paginator = Paginator(queryset, 2) # количество постов на странице
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    context = {'page_obj': page_obj, 'form': form} # Передаем форму в контекст
    return render(request, 'blog/index.html', context)

from django.shortcuts import render
def show_sql(request):
    if request.method == 'POST':
        print("1111")
        pass
    return render(request, 'index.html')


def execute_sql(request):
    try:
        # Выполнение SQL-запроса
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM blog_location")
            rows = cursor.fetchall()

        # Формирование ответа
        data = [{'id': row[0], 'is_published': row[1], 'created_at': row[2], 'name': row[3]} for row in rows]
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_dishes_html():
    with connection.cursor() as cursor:
        # Вызов хранимой функции для получения HTML-кода
        cursor.execute("SELECT get_dishes_html()")
        result = cursor.fetchone()
    
    # Проверяем, есть ли результат и возвращаем строчку без лишних пробелов
    if result and result[0]:
        return result[0].strip()  # Возвращаем чистый HTML
    return ''
