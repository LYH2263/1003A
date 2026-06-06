from django.db import models
from django.utils import timezone
from apps.users.models import User
import json

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="分类名称")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="父级分类")
    
    def __str__(self):
        return self.name
    
    def is_top_level(self):
        return self.parent is None
    
    def get_full_name(self):
        if self.parent:
            return f"{self.parent.name}/{self.name}"
        return self.name
    
    def get_book_count(self):
        if self.is_top_level():
            return Book.objects.filter(category__parent=self).count()
        return self.book_set.count()
    
    def can_delete(self):
        if self.is_top_level():
            return not self.children.exists() and not Book.objects.filter(category__parent=self).exists()
        return not self.book_set.exists()
        
    class Meta:
        verbose_name = "图书分类"
        verbose_name_plural = verbose_name
        ordering = ['id']

class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name="书名")
    author = models.CharField(max_length=50, verbose_name="作者")
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="分类")
    description = models.TextField(blank=True, verbose_name="简介")
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name="封面")
    stock = models.PositiveIntegerField(default=0, verbose_name="当前库存")
    total_stock = models.PositiveIntegerField(default=0, verbose_name="总库存")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
        
    class Meta:
        verbose_name = "图书"
        verbose_name_plural = verbose_name

class LoanRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('rejected', '已拒绝'),
        ('pending_payment', '待缴费'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="借阅人")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="图书")
    borrow_date = models.DateField(auto_now_add=True, verbose_name="申请日期")
    due_date = models.DateField(verbose_name="应还日期")
    return_date = models.DateField(null=True, blank=True, verbose_name="归还日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="罚款金额")
    fine_paid = models.BooleanField(default=False, verbose_name="罚款已缴纳")
    fine_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.5, verbose_name="每日罚款单价")
    payment_date = models.DateField(null=True, blank=True, verbose_name="缴费日期")
    borrow_rule_snapshot = models.TextField(default='{}', verbose_name="借阅规则快照")
    renew_count = models.PositiveIntegerField(default=0, verbose_name="续借次数")
    
    class Meta:
        ordering = ['-borrow_date']
        verbose_name = "借阅记录"
        verbose_name_plural = verbose_name
        
    def get_borrow_rule(self):
        try:
            return json.loads(self.borrow_rule_snapshot)
        except:
            return {}
    
    def can_renew(self):
        rule = self.get_borrow_rule()
        if not rule or not rule.get('allow_renew', False):
            return False
        max_renew = rule.get('max_renew_count', 0)
        if self.renew_count >= max_renew:
            return False
        if self.status != 'borrowed':
            return False
        from datetime import date
        if date.today() > self.due_date:
            return False
        return True

    def is_overdue(self):
        from datetime import date
        if self.status == 'borrowed' and date.today() > self.due_date:
            return True
        return False
    
    def calculate_fine(self):
        from datetime import date
        if self.status == 'returned' or self.status == 'pending_payment':
            return float(self.fine_amount)
        if self.status == 'borrowed':
            today = date.today()
            if today > self.due_date:
                overdue_days = (today - self.due_date).days
                return overdue_days * float(self.fine_daily_rate)
        return 0
    
    def get_overdue_days(self):
        from datetime import date
        if self.status == 'pending_payment' and self.return_date:
            if self.return_date > self.due_date:
                return (self.return_date - self.due_date).days
            return 0
        if self.status == 'borrowed':
            today = date.today()
            if today > self.due_date:
                return (today - self.due_date).days
        return 0

class Announcement(models.Model):
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    is_active = models.BooleanField(default=True, verbose_name="是否显示")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class SiteConfig(models.Model):
    site_title = models.CharField(max_length=50, default="龙猫图书管理系统", verbose_name="系统名称")
    maintenance_mode = models.BooleanField(default=False, verbose_name="维护模式")
    daily_fine_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.5, verbose_name="每日罚款单价(元)")
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteConfig.objects.exists():
            return
        super().save(*args, **kwargs)
        
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class BorrowRule(models.Model):
    name = models.CharField(max_length=100, verbose_name="规则名称")
    max_borrow_days = models.PositiveIntegerField(default=30, verbose_name="最大借阅天数")
    max_borrow_quantity = models.PositiveIntegerField(default=0, verbose_name="每人最大同时借阅数量", help_text="0表示无限制")
    max_daily_requests = models.PositiveIntegerField(default=0, verbose_name="每日最大申请次数", help_text="0表示无限制")
    allow_renew = models.BooleanField(default=True, verbose_name="是否允许续借")
    max_renew_count = models.PositiveIntegerField(default=1, verbose_name="最大续借次数")
    renew_days = models.PositiveIntegerField(default=15, verbose_name="续借天数")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ['-is_active', '-created_at']
        verbose_name = "借阅规则"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @classmethod
    def get_active_rule(cls):
        return cls.objects.filter(is_active=True).first()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_borrow_days': self.max_borrow_days,
            'max_borrow_quantity': self.max_borrow_quantity,
            'max_daily_requests': self.max_daily_requests,
            'allow_renew': self.allow_renew,
            'max_renew_count': self.max_renew_count,
            'renew_days': self.renew_days,
        }

    def get_rule_summary(self):
        summary = f"借期{self.max_borrow_days}天"
        if self.allow_renew:
            summary += f"，可续借{self.max_renew_count}次"
        if self.max_borrow_quantity > 0:
            summary += f"，限借{self.max_borrow_quantity}本"
        if self.max_daily_requests > 0:
            summary += f"，每日限申{self.max_daily_requests}次"
        return summary

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('waiting', '排队中'),
        ('notified', '已通知'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
        ('expired', '已过期'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="预约人")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="图书")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name="状态")
    queue_position = models.PositiveIntegerField(default=0, verbose_name="排队位置")
    notified_at = models.DateTimeField(null=True, blank=True, verbose_name="通知时间")
    expire_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="预约时间")
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "预约记录"
        verbose_name_plural = verbose_name
        unique_together = ['user', 'book', 'status']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            waiting_count = Reservation.objects.filter(book=self.book, status='waiting').count()
            self.queue_position = waiting_count + 1
        super().save(*args, **kwargs)
    
    def cancel(self):
        self.status = 'cancelled'
        self.save()
        Reservation.update_queue_positions(self.book)
    
    @staticmethod
    def update_queue_positions(book):
        waiting_reservations = Reservation.objects.filter(book=book, status='waiting').order_by('created_at')
        for idx, res in enumerate(waiting_reservations, 1):
            if res.queue_position != idx:
                res.queue_position = idx
                res.save(update_fields=['queue_position'])
    
    def is_expired(self):
        if self.expire_at and timezone.now() > self.expire_at:
            return True
        return False
    
    @staticmethod
    def notify_next_reader(book):
        waiting_reservations = Reservation.objects.filter(book=book, status='waiting').order_by('created_at')
        if waiting_reservations.exists():
            next_reservation = waiting_reservations.first()
            next_reservation.status = 'notified'
            next_reservation.notified_at = timezone.now()
            next_reservation.expire_at = timezone.now() + timezone.timedelta(hours=48)
            next_reservation.save()
            Reservation.update_queue_positions(book)
            
            Announcement.objects.create(
                title=f"预约到货通知：《{book.title}》",
                content=f"尊敬的 {next_reservation.user.username}，您预约的图书《{book.title}》现已可借阅。请在48小时内发起借阅申请，逾期将自动取消您的预约资格。",
                is_active=True
            )
            return next_reservation
        return None

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='图书')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name='评论者')
    rating = models.PositiveSmallIntegerField(verbose_name='评分')
    content = models.TextField(max_length=500, verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '书评'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}星)"
    
    def get_replies(self):
        return self.replies.all().order_by('created_at')

class ReviewReply(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies', verbose_name='所属评论')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_replies', verbose_name='回复者')
    content = models.TextField(max_length=500, verbose_name='回复内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='回复时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '评论回复'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} 回复 {self.review.user.username}"

class BookList(models.Model):
    VISIBILITY_CHOICES = (
        ('private', '私密'),
        ('public', '公开'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_lists', verbose_name='创建者')
    name = models.CharField(max_length=100, verbose_name='书单名称')
    description = models.TextField(blank=True, max_length=500, verbose_name='简短描述')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private', verbose_name='可见性')
    share_token = models.CharField(max_length=32, unique=True, null=True, blank=True, verbose_name='分享令牌')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '书单'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def book_count(self):
        return self.entries.count()
    
    def generate_share_token(self):
        import uuid
        if not self.share_token:
            self.share_token = uuid.uuid4().hex
            self.save()
        return self.share_token

class BookListEntry(models.Model):
    book_list = models.ForeignKey(BookList, on_delete=models.CASCADE, related_name='entries', verbose_name='所属书单')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='list_entries', verbose_name='图书')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        ordering = ['-added_at']
        verbose_name = '书单条目'
        verbose_name_plural = verbose_name
        unique_together = ['book_list', 'book']
    
    def __str__(self):
        return f"{self.book_list.name} - {self.book.title}"
