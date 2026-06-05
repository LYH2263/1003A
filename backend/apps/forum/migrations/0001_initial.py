from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0007_booklist_booklistentry'),
        ('users', '0002_credit_system'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='板块名称')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('sort_weight', models.IntegerField(default=0, verbose_name='排序权重')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '论坛板块',
                'verbose_name_plural': '论坛板块',
                'ordering': ['sort_weight', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('content', models.TextField(verbose_name='内容')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='浏览数')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='置顶标记')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_posts', to='users.user', verbose_name='作者')),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forum_posts', to='books.book', verbose_name='关联图书')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='forum.forumcategory', verbose_name='板块')),
            ],
            options={
                'verbose_name': '帖子',
                'verbose_name_plural': '帖子',
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forum_replies', to='users.user', verbose_name='作者')),
                ('parent_reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_replies', to='forum.reply', verbose_name='引用回复')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='forum.post', verbose_name='所属帖子')),
            ],
            options={
                'verbose_name': '回复',
                'verbose_name_plural': '回复',
                'ordering': ['created_at'],
            },
        ),
    ]
