from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_reservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanrecord',
            name='fine_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='罚款金额'),
        ),
        migrations.AddField(
            model_name='loanrecord',
            name='fine_daily_rate',
            field=models.DecimalField(decimal_places=2, default=0.5, max_digits=10, verbose_name='每日罚款单价'),
        ),
        migrations.AddField(
            model_name='loanrecord',
            name='fine_paid',
            field=models.BooleanField(default=False, verbose_name='罚款已缴纳'),
        ),
        migrations.AddField(
            model_name='loanrecord',
            name='payment_date',
            field=models.DateField(blank=True, null=True, verbose_name='缴费日期'),
        ),
        migrations.AlterField(
            model_name='loanrecord',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', '待审核'),
                    ('borrowed', '借阅中'),
                    ('returned', '已归还'),
                    ('rejected', '已拒绝'),
                    ('pending_payment', '待缴费')
                ],
                default='pending',
                max_length=20,
                verbose_name='状态'
            ),
        ),
        migrations.AddField(
            model_name='siteconfig',
            name='daily_fine_rate',
            field=models.DecimalField(decimal_places=2, default=0.5, max_digits=10, verbose_name='每日罚款单价(元)'),
        ),
    ]
