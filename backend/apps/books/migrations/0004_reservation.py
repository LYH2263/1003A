from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('books', '0003_siteconfig_alter_announcement_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('waiting', '排队中'), ('notified', '已通知'), ('completed', '已完成'), ('cancelled', '已取消'), ('expired', '已过期')], default='waiting', max_length=20, verbose_name='状态')),
                ('queue_position', models.PositiveIntegerField(default=0, verbose_name='排队位置')),
                ('notified_at', models.DateTimeField(blank=True, null=True, verbose_name='通知时间')),
                ('expire_at', models.DateTimeField(blank=True, null=True, verbose_name='过期时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='预约时间')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book', verbose_name='图书')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='预约人')),
            ],
            options={
                'verbose_name': '预约记录',
                'verbose_name_plural': '预约记录',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.UniqueConstraint(fields=['user', 'book', 'status'], name='unique_user_book_active_reservation'),
        ),
    ]
