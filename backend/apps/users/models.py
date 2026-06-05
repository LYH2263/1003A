from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('reader', '读者'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader', verbose_name='角色')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    credit_score = models.IntegerField(default=100, verbose_name='信用积分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def update_credit(self, points, reason, operator=None):
        self.credit_score = max(0, min(100, self.credit_score + points))
        self.save()
        CreditLog.objects.create(
            user=self,
            points=points,
            balance_after=self.credit_score,
            reason=reason,
            operator=operator
        )

    def can_borrow(self):
        return self.credit_score >= 60

class CreditLog(models.Model):
    TYPE_CHOICES = (
        ('return_on_time', '按时归还'),
        ('return_early', '提前归还'),
        ('return_late', '逾期归还'),
        ('manual_add', '手动加分'),
        ('manual_subtract', '手动扣分'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_logs', verbose_name='用户')
    points = models.IntegerField(verbose_name='变动积分')
    balance_after = models.IntegerField(verbose_name='变动后积分')
    reason = models.CharField(max_length=200, verbose_name='变动原因')
    log_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='manual_add', verbose_name='类型')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_operations', verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '信用积分日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}: {'+' if self.points > 0 else ''}{self.points}分"
