from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_review_reviewreply'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='书单名称')),
                ('description', models.TextField(blank=True, max_length=500, verbose_name='简短描述')),
                ('visibility', models.CharField(choices=[('private', '私密'), ('public', '公开')], default='private', max_length=20, verbose_name='可见性')),
                ('share_token', models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='分享令牌')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_lists', to='users.user', verbose_name='创建者')),
            ],
            options={
                'verbose_name': '书单',
                'verbose_name_plural': '书单',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='BookListEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='list_entries', to='books.book', verbose_name='图书')),
                ('book_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='books.booklist', verbose_name='所属书单')),
            ],
            options={
                'verbose_name': '书单条目',
                'verbose_name_plural': '书单条目',
                'ordering': ['-added_at'],
                'unique_together': {('book_list', 'book')},
            },
        ),
    ]
