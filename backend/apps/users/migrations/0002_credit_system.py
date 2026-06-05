from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='credit_score',
            field=models.IntegerField(default=100, verbose_name='信用积分'),
        ),
        migrations.CreateModel(
            name='CreditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(verbose_name='变动积分')),
                ('balance_after', models.IntegerField(verbose_name='变动后积分')),
                ('reason', models.CharField(max_length=200, verbose_name='变动原因')),
                ('log_type', models.CharField(choices=[('return_on_time', '按时归还'), ('return_early', '提前归还'), ('return_late', '逾期归还'), ('manual_add', '手动加分'), ('manual_subtract', '手动扣分')], default='manual_add', max_length=20, verbose_name='类型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='操作时间')),
                ('operator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='credit_operations', to='users.user', verbose_name='操作人')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credit_logs', to='users.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '信用积分日志',
                'verbose_name_plural': '信用积分日志',
                'ordering': ['-created_at'],
            },
        ),
    ]
