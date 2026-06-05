from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import ForumCategory, Post, Reply
from apps.books.models import Book


def forum_home(request):
    categories = ForumCategory.objects.all()
    
    total_posts = Post.objects.count()
    today = timezone.now().date()
    today_posts = Post.objects.filter(created_at__date=today).count()
    active_users = Post.objects.values('author').distinct().count()
    
    context = {
        'categories': categories,
        'total_posts': total_posts,
        'today_posts': today_posts,
        'active_users': active_users,
    }
    return render(request, 'forum/home.html', context)


def category_detail(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id)
    posts = Post.objects.filter(category=category)
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts_page,
    }
    return render(request, 'forum/category.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    viewed_posts = request.session.get('viewed_posts', {})
    post_id_str = str(post_id)
    current_time = timezone.now().timestamp()
    
    if post_id_str not in viewed_posts or (current_time - viewed_posts[post_id_str]) > 3600:
        post.views += 1
        post.save()
        viewed_posts[post_id_str] = current_time
        request.session['viewed_posts'] = viewed_posts
    
    replies = Reply.objects.filter(post=post).select_related('author', 'parent_reply', 'parent_reply__author')
    
    paginator = Paginator(replies, 20)
    page = request.GET.get('page', 1)
    replies_page = paginator.get_page(page)
    
    reply_floor_offset = (replies_page.number - 1) * paginator.per_page
    
    context = {
        'post': post,
        'replies': replies_page,
        'reply_floor_offset': reply_floor_offset,
    }
    return render(request, 'forum/post_detail.html', context)


@login_required
def create_post(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id)
    books = Book.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        book_id = request.POST.get('book')
        
        if not title or not content:
            messages.error(request, '标题和内容不能为空。')
        else:
            book = None
            if book_id:
                book = Book.objects.filter(id=book_id).first()
            
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                category=category,
                book=book
            )
            messages.success(request, '发帖成功！')
            return redirect('post_detail', post_id=post.id)
    
    context = {
        'category': category,
        'books': books,
    }
    return render(request, 'forum/create_post.html', context)


@login_required
def create_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_reply_id = request.POST.get('parent_reply')
        
        if not content:
            messages.error(request, '回复内容不能为空。')
        else:
            parent_reply = None
            if parent_reply_id:
                parent_reply = Reply.objects.filter(id=parent_reply_id, post=post).first()
            
            Reply.objects.create(
                post=post,
                content=content,
                author=request.user,
                parent_reply=parent_reply
            )
            messages.success(request, '回复成功！')
            return redirect('post_detail', post_id=post.id)
    
    return redirect('post_detail', post_id=post.id)


@login_required
def toggle_pin_post(request, post_id):
    if request.user.role != 'admin':
        messages.error(request, '没有权限执行此操作。')
        return redirect('home')
    
    post = get_object_or_404(Post, id=post_id)
    post.is_pinned = not post.is_pinned
    post.save()
    
    action = '置顶' if post.is_pinned else '取消置顶'
    messages.success(request, f'帖子已{action}。')
    return redirect('post_detail', post_id=post.id)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author and request.user.role != 'admin':
        messages.error(request, '没有权限编辑此帖子。')
        return redirect('post_detail', post_id=post.id)
    
    books = Book.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        book_id = request.POST.get('book')
        
        if not title or not content:
            messages.error(request, '标题和内容不能为空。')
        else:
            book = None
            if book_id:
                book = Book.objects.filter(id=book_id).first()
            
            post.title = title
            post.content = content
            post.book = book
            post.save()
            
            messages.success(request, '帖子已更新。')
            return redirect('post_detail', post_id=post.id)
    
    context = {
        'post': post,
        'books': books,
    }
    return render(request, 'forum/edit_post.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author and request.user.role != 'admin':
        messages.error(request, '没有权限执行此操作。')
        return redirect('home')
    
    category_id = post.category.id
    post.delete()
    
    messages.success(request, '帖子已删除。')
    return redirect('category_detail', category_id=category_id)


@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    
    if request.user != reply.author and request.user.role != 'admin':
        messages.error(request, '没有权限执行此操作。')
        return redirect('home')
    
    post_id = reply.post.id
    reply.delete()
    
    messages.success(request, '回复已删除。')
    return redirect('post_detail', post_id=post_id)
