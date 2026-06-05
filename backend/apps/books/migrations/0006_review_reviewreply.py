from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_fine_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(verbose_name='评分')),
                ('content', models.TextField(max_length=500, verbose_name='评论内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='books.book', verbose_name='图书')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='users.user', verbose_name='评论者')),
            ],
            options={
                'verbose_name': '书评',
                'verbose_name_plural': '书评',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReviewReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=500, verbose_name='回复内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='回复时间')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='books.review', verbose_name='所属评论')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_replies', to='users.user', verbose_name='回复者')),
            ],
            options={
                'verbose_name': '评论回复',
                'verbose_name_plural': '评论回复',
                'ordering': ['created_at'],
            },
        ),
    ]
