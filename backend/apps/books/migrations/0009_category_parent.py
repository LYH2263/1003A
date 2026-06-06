from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_borrowrule_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name='children',
                to='books.category',
                verbose_name='父级分类'
            ),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id'], 'verbose_name': '图书分类', 'verbose_name_plural': '图书分类'},
        ),
    ]
