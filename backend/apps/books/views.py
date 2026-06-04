from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Book, LoanRecord, Announcement, Category, SiteConfig
from apps.users.models import User
from datetime import date, timedelta
from django.utils import timezone

# ... (Previous simple views: home, admin_dashboard)

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    stats = {
        'total_books': Book.objects.count(),
        'total_users': User.objects.count(),
        'active_loans': LoanRecord.objects.filter(status='borrowed').count(),
        'pending_requests': LoanRecord.objects.filter(status='pending').count(),
    }
    
    recent_loans = LoanRecord.objects.all().order_by('-borrow_date')[:5]
    return render(request, 'admin/dashboard.html', {'stats': stats, 'recent_loans': recent_loans})

@login_required
def dashboard_chart_data(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    today = timezone.now().date()
    
    # Weekly Data: Last 7 days
    weekly_labels = []
    weekly_data = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        weekly_labels.append(target_date.strftime('%m-%d'))
        count = LoanRecord.objects.filter(borrow_date=target_date).count()
        weekly_data.append(count)
        
    # Monthly Data: Last 4 weeks (simplified approach: 4 segments of 7 days)
    monthly_labels = ['前四周', '前三周', '前两周', '本周']
    monthly_data = []
    for i in range(3, -1, -1):
        start_date = today - timedelta(days=(i * 7) + 6)
        end_date = today - timedelta(days=i * 7)
        count = LoanRecord.objects.filter(borrow_date__range=[start_date, end_date]).count()
        monthly_data.append(count)
        
    return JsonResponse({
        'weekly': {
            'labels': weekly_labels,
            'data': weekly_data
        },
        'monthly': {
            'labels': monthly_labels,
            'data': monthly_data
        }
    })

@login_required
def book_manage(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    query = request.GET.get('q', '')
    books_list = Book.objects.all().order_by('-created_at')
    
    if query:
        books_list = books_list.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    
    paginator = Paginator(books_list, 10)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    return render(request, 'admin/book_list.html', {'books': books, 'categories': categories})

@login_required
def book_create(request):
    if request.user.role != 'admin':
        return redirect('home')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        isbn = request.POST.get('isbn')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        total_stock = int(request.POST.get('total_stock', 0))
        cover = request.FILES.get('cover')
        
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, "ISBN 已存在，请检查输入。")
        else:
            category = Category.objects.get(pk=category_id) if category_id else None
            Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                description=description,
                stock=total_stock, # Initial stock equals total stock
                total_stock=total_stock,
                cover=cover
            )
            messages.success(request, f"图书《{title}》已成功上架。")
    
    return redirect('book_manage')

@login_required
def book_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
        
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        # ISBN typically shouldn't be changed easily or needs validation, but allowing for correction
        new_isbn = request.POST.get('isbn')
        if new_isbn != book.isbn and Book.objects.filter(isbn=new_isbn).exists():
             messages.error(request, "新的 ISBN 已存在。")
             return redirect('book_manage')
             
        book.isbn = new_isbn
        category_id = request.POST.get('category')
        book.category = Category.objects.get(pk=category_id) if category_id else None
        book.description = request.POST.get('description')
        
        # Stock logic: Update total. If total increases, increase current stock.
        new_total = int(request.POST.get('total_stock', 0))
        diff = new_total - book.total_stock
        book.total_stock = new_total
        book.stock += diff
        
        if request.FILES.get('cover'):
            book.cover = request.FILES.get('cover')
            
        book.save()
        messages.success(request, f"图书《{book.title}》信息已更新。")
        
    return redirect('book_manage')

@login_required
def book_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, f"图书《{book.title}》已成功删除。")
    return redirect('book_manage')

# ... (Keep existing loan_manage, book_browse, book_detail, borrow_request, my_loans, user_manage, audit_loan, system_settings, etc.)
@login_required
def loan_manage(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    loans_list = LoanRecord.objects.all().order_by('-borrow_date')
    
    # Filtering
    status = request.GET.get('status')
    user_query = request.GET.get('user')
    
    if status:
        loans_list = loans_list.filter(status=status)
    if user_query:
        loans_list = loans_list.filter(user__username__icontains=user_query)
        
    paginator = Paginator(loans_list, 10)
    page_number = request.GET.get('page')
    loans = paginator.get_page(page_number)
    
    return render(request, 'admin/loan_list.html', {'loans': loans})

@login_required
def book_browse(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    if category_id:
        books = books.filter(category_id=category_id)
        
    categories = Category.objects.all()
    return render(request, 'books/browse.html', {'books': books, 'categories': categories, 'query': query})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/detail.html', {'book': book})

@login_required
def borrow_request(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.stock <= 0:
        messages.error(request, "该图书目前无库存，无法借阅。")
        return redirect('book_detail', pk=pk)
        
    if LoanRecord.objects.filter(user=request.user, book=book, status__in=['pending', 'borrowed']).exists():
        messages.warning(request, "您已申请或正在借阅此书，请勿重复操作。")
        return redirect('book_detail', pk=pk)
        
    # Create request
    LoanRecord.objects.create(
        user=request.user,
        book=book,
        due_date=date.today() + timedelta(days=30),
        status='pending'
    )
    messages.success(request, "借阅申请已提交，请等待管理员审核。")
    return redirect('my_loans')

@login_required
def my_loans(request):
    loans = LoanRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'user/my_loans.html', {'loans': loans})
    
@login_required
def user_manage(request):
    if request.user.role != 'admin':
        return redirect('home')
    users = User.objects.all().exclude(pk=request.user.pk)
    return render(request, 'admin/user_list.html', {'users': users})

@login_required
def audit_loan(request, pk, action):
    if request.user.role != 'admin':
        return redirect('home')
    loan = get_object_or_404(LoanRecord, pk=pk)
    
    if action == 'approve':
        if loan.book.stock > 0:
            loan.status = 'borrowed'
            loan.book.stock -= 1
            loan.book.save()
            loan.save()
            messages.success(request, "借阅申请已批准。")
        else:
            messages.error(request, "库存不足，无法批准。")
    elif action == 'reject':
        loan.status = 'rejected'
        loan.save()
        messages.success(request, "借阅申请已拒绝。")
    elif action == 'return':
        loan.status = 'returned'
        loan.return_date = date.today()
        loan.book.stock += 1
        loan.book.save()
        loan.save()
        messages.success(request, "图书已成功归还。")
        
    return redirect('loan_manage')
    
@login_required
def system_settings(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    config = SiteConfig.get_solo()
    
    if request.method == 'POST':
        # ... (Keep existing logic)
        action = request.POST.get('action')
        if action == 'update_config':
            config.site_title = request.POST.get('site_title')
            config.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            config.save()
            messages.success(request, "系统基本配置已更新。")
        elif action == 'create_announcement':
            title = request.POST.get('title')
            content = request.POST.get('content')
            Announcement.objects.create(title=title, content=content)
            messages.success(request, "公告发布成功。")
            return redirect('system_settings')
            
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'admin/settings.html', {'announcements': announcements, 'config': config})

@login_required
def announcement_delete(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    Announcement.objects.filter(pk=pk).delete()
    messages.success(request, "公告已删除")
    return redirect('system_settings')

@login_required
def announcement_create(request):
    return redirect('system_settings')
    
# Helper function
def home(request): # Re-definition at the end to catch all context? No, just ensuring clean file content in write_to_file
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
    latest_books = Book.objects.all().order_by('-created_at')[:8]
    config = SiteConfig.get_solo()
    return render(request, 'books/home.html', {
        'announcements': announcements,
        'latest_books': latest_books,
        'config': config
    })
