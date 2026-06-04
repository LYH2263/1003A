from django.db import models
from apps.users.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="分类名称")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "图书分类"
        verbose_name_plural = verbose_name

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
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="借阅人")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="图书")
    borrow_date = models.DateField(auto_now_add=True, verbose_name="申请日期")
    due_date = models.DateField(verbose_name="应还日期")
    return_date = models.DateField(null=True, blank=True, verbose_name="归还日期")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    
    class Meta:
        ordering = ['-borrow_date']
        verbose_name = "借阅记录"
        verbose_name_plural = verbose_name

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
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteConfig.objects.exists():
            return
        super().save(*args, **kwargs)
        
    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
