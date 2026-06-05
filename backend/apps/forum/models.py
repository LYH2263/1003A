from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.books.models import Book


class ForumCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name='板块名称')
    description = models.TextField(blank=True, verbose_name='描述')
    sort_weight = models.IntegerField(default=0, verbose_name='排序权重')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['sort_weight', '-created_at']
        verbose_name = '论坛板块'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def post_count(self):
        return self.posts.count()

    def latest_post(self):
        return self.posts.order_by('-created_at').first()


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts', verbose_name='作者')
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='posts', verbose_name='板块')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='forum_posts', verbose_name='关联图书')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览数')
    is_pinned = models.BooleanField(default=False, verbose_name='置顶标记')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = '帖子'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def reply_count(self):
        return self.replies.count()

    def latest_reply(self):
        return self.replies.order_by('-created_at').first()

    def increment_views(self):
        self.views = models.F('views') + 1
        self.save()


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies', verbose_name='所属帖子')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies', verbose_name='作者')
    parent_reply = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_replies', verbose_name='引用回复')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['created_at']
        verbose_name = '回复'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.author.username} - {self.post.title[:20]}'

    def get_floor(self):
        return Reply.objects.filter(post=self.post, created_at__lte=self.created_at).count()
