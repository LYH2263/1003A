import os
import django
import random
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.users.models import User
from apps.books.models import Book, Category, LoanRecord, Announcement

def seed():
    print("开始填充演示数据...")

    # 1. 创建管理员和普通用户
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        admin.set_password('123456')
        admin.save()
        print("- 管理员账户创建成功: admin / 123456")

    reader, created = User.objects.get_or_create(
        username='reader1',
        defaults={'role': 'reader', 'phone': '13800000000'}
    )
    if created:
        reader.set_password('123456')
        reader.save()
        print("- 普通读者账户创建成功: reader1 / 123456")

    # 2. 创建图书分类
    categories_names = ['经典文学', '科学技术', '历史哲学', '艺术教育', '由于规则而生的书籍']
    categories = []
    for name in categories_names:
        cat, _ = Category.objects.get_or_create(name=name)
        categories.append(cat)
    print(f"- 已同步 {len(categories)} 个图书分类")

    # 3. 创建图书
    book_data = [
        ('解忧杂货店', '东野圭吾', '9787544270878', '这是一部治愈系的神作。', 10, categories[0]),
        ('三体', '刘慈欣', '9787229030933', '中国科幻的巅峰之作。', 5, categories[1]),
        ('人类简史', '尤瓦尔·赫拉利', '9787508647357', '理清人类文明的脉络。', 8, categories[2]),
        ('设计心理学', '唐纳德·诺曼', '9787508650388', '了解产品设计的核心逻辑。', 3, categories[3]),
        ('活着', '余华', '9787506365437', '平凡生命在苦难中的坚守。', 12, categories[0]),
        ('百年孤独', '加西亚·马尔克斯', '9787544253994', '魔幻现实主义的巅峰。', 0, categories[0]), # 无库存演示
    ]
    
    for title, author, isbn, desc, stock, cat in book_data:
        Book.objects.get_or_create(
            isbn=isbn,
            defaults={
                'title': title,
                'author': author,
                'description': desc,
                'category': cat,
                'stock': stock,
                'total_stock': stock + 5
            }
        )
    print(f"- 已成功上架 {len(book_data)} 本图书")

    # 4. 创建系统公告
    announcements = [
        ('春节期间闭馆通知', '因春节假期，本馆将于2月10日至2月17日闭馆，请广大读者悉知。'),
        ('新书入库预告', '本月底将新增 200 余本计算机类专业书籍，欢迎大家借阅。'),
        ('阅读推广活动', '参与“共读一本书”活动，赢取精美周边礼品。'),
    ]
    for title, content in announcements:
        Announcement.objects.get_or_create(title=title, defaults={'content': content})
    print("- 系统公告已更新")

    # 5. 创建演示借阅记录
    if not LoanRecord.objects.exists():
        book = Book.objects.first()
        LoanRecord.objects.create(
            user=reader,
            book=book,
            due_date=date.today() + timedelta(days=30),
            status='borrowed'
        )
        print("- 已生成演示借阅记录")

    print("数据填充完成！")

if __name__ == "__main__":
    seed()
