from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Book, LoanRecord, Announcement, Category, SiteConfig, Reservation
from apps.users.models import User, CreditLog
from datetime import date, timedelta
from django.utils import timezone

# ... (Previous simple views: home, admin_dashboard)

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    from django.db.models import Sum
    from datetime import datetime
    
    today = date.today()
    first_day_of_month = today.replace(day=1)
    
    pending_payments = LoanRecord.objects.filter(status='pending_payment')
    total_pending_fine = sum(loan.calculate_fine() for loan in pending_payments)
    
    paid_this_month = LoanRecord.objects.filter(
        payment_date__gte=first_day_of_month,
        fine_paid=True
    ).aggregate(total=Sum('fine_amount'))['total'] or 0
    
    stats = {
        'total_books': Book.objects.count(),
        'total_users': User.objects.count(),
        'active_loans': LoanRecord.objects.filter(status='borrowed').count(),
        'pending_requests': LoanRecord.objects.filter(status='pending').count(),
        'pending_payments': pending_payments.count(),
        'monthly_fine_total': float(paid_this_month) + total_pending_fine,
        'monthly_fine_paid': float(paid_this_month),
        'monthly_fine_unpaid': total_pending_fine,
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
    
    check_expired_reservations()
    
    query = request.GET.get('q', '')
    books_list = Book.objects.all().order_by('-created_at')
    
    if query:
        books_list = books_list.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query))
    
    paginator = Paginator(books_list, 10)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    reservation_counts = {}
    for book in books:
        count = Reservation.objects.filter(book=book, status__in=['waiting', 'notified']).count()
        reservation_counts[book.id] = count
    
    categories = Category.objects.all()
    return render(request, 'admin/book_list.html', {
        'books': books,
        'categories': categories,
        'reservation_counts': reservation_counts
    })

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
    
    check_expired_reservations()
    
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
    
    reservation_counts = {}
    for loan in loans:
        count = Reservation.objects.filter(book=loan.book, status='waiting').count()
        reservation_counts[loan.book.id] = count
    
    return render(request, 'admin/loan_list.html', {
        'loans': loans,
        'reservation_counts': reservation_counts
    })

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
    user_reservation = None
    queue_count = 0
    if request.user.is_authenticated:
        user_reservation = Reservation.objects.filter(
            user=request.user,
            book=book,
            status__in=['waiting', 'notified']
        ).first()
        queue_count = Reservation.objects.filter(book=book, status='waiting').count()
    return render(request, 'books/detail.html', {
        'book': book,
        'user_reservation': user_reservation,
        'queue_count': queue_count
    })

@login_required
def join_reservation(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if book.stock > 0:
        messages.warning(request, "该书仍有库存，可直接借阅。")
        return redirect('book_detail', pk=pk)
    
    existing = Reservation.objects.filter(
        user=request.user,
        book=book,
        status__in=['waiting', 'notified']
    ).first()
    
    if existing:
        if existing.status == 'notified':
            messages.warning(request, "您已收到预约到货通知，请在48小时内发起借阅。")
        else:
            messages.warning(request, "您已在排队中。")
        return redirect('book_detail', pk=pk)
    
    Reservation.objects.create(
        user=request.user,
        book=book
    )
    messages.success(request, "成功加入预约队列！图书到货后将按顺序通知您。")
    return redirect('book_detail', pk=pk)

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    book = reservation.book
    
    if reservation.status in ['waiting', 'notified']:
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, "预约已取消。")
    
    return redirect('book_detail', pk=book.pk)

@login_required
def reservation_queue(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    book = get_object_or_404(Book, pk=pk)
    reservations = Reservation.objects.filter(book=book, status__in=['waiting', 'notified']).order_by('created_at')
    return render(request, 'admin/reservation_queue.html', {'book': book, 'reservations': reservations})

@login_required
def remove_reservation(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    reservation = get_object_or_404(Reservation, pk=pk)
    book_pk = reservation.book.pk
    reservation.status = 'cancelled'
    reservation.save()
    messages.success(request, f"已移除 {reservation.user.username} 的预约。")
    return redirect('reservation_queue', pk=book_pk)

def check_expired_reservations():
    now = timezone.now()
    expired = Reservation.objects.filter(status='notified', expire_at__lte=now)
    for res in expired:
        res.status = 'expired'
        res.save()
        Reservation.notify_next_reader(res.book)

@login_required
def borrow_request(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    check_expired_reservations()
    
    if LoanRecord.objects.filter(user=request.user, status='pending_payment').exists():
        messages.error(request, "您存在未缴纳的逾期罚款，请先缴费后再申请借阅。")
        return redirect('my_loans')
    
    if book.stock <= 0:
        messages.error(request, "该图书目前无库存，无法借阅。")
        return redirect('book_detail', pk=pk)
        
    if not request.user.can_borrow():
        messages.error(request, f"信用不足，暂停借阅。当前信用分：{request.user.credit_score}，需≥60分方可借阅。")
        return redirect('book_detail', pk=pk)
        
    if LoanRecord.objects.filter(user=request.user, book=book, status__in=['pending', 'borrowed']).exists():
        messages.warning(request, "您已申请或正在借阅此书，请勿重复操作。")
        return redirect('book_detail', pk=pk)
    
    reservation = Reservation.objects.filter(
        user=request.user,
        book=book,
        status='notified'
    ).first()
    
    config = SiteConfig.get_solo()
    LoanRecord.objects.create(
        user=request.user,
        book=book,
        due_date=date.today() + timedelta(days=30),
        status='pending',
        fine_daily_rate=config.daily_fine_rate
    )
    
    if reservation:
        reservation.status = 'completed'
        reservation.save()
    
    messages.success(request, "借阅申请已提交，请等待管理员审核。")
    return redirect('my_loans')

@login_required
def my_loans(request):
    check_expired_reservations()
    loans = LoanRecord.objects.filter(user=request.user).order_by('-borrow_date')
    
    loans_with_fine = []
    for loan in loans:
        loan.current_fine = loan.calculate_fine()
        loan.overdue_days = loan.get_overdue_days()
        loans_with_fine.append(loan)
    
    reservations = Reservation.objects.filter(
        user=request.user,
        status__in=['waiting', 'notified']
    ).order_by('-created_at')
    return render(request, 'user/my_loans.html', {
        'loans': loans_with_fine,
        'reservations': reservations
    })
    
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
        loan.return_date = date.today()
        loan.book.stock += 1
        loan.book.save()
        
        days_diff = (loan.due_date - loan.return_date).days
        if days_diff >= 7:
            points = 3
            log_type = 'return_early'
            reason = f'提前归还《{loan.book.title}》，提前{days_diff}天'
            loan.status = 'returned'
            loan.fine_paid = True
        elif days_diff >= 0:
            points = 1
            log_type = 'return_on_time'
            reason = f'按时归还《{loan.book.title}》'
            loan.status = 'returned'
            loan.fine_paid = True
        else:
            late_days = abs(days_diff)
            points = -(late_days * 2)
            log_type = 'return_late'
            reason = f'逾期归还《{loan.book.title}》，逾期{late_days}天'
            fine_amount = late_days * float(loan.fine_daily_rate)
            loan.fine_amount = fine_amount
            loan.status = 'pending_payment'
            loan.fine_paid = False
        
        loan.save()
        
        loan.user.update_credit(points, reason, request.user)
        CreditLog.objects.filter(user=loan.user, reason=reason).update(log_type=log_type)
        
        notified_reservation = Reservation.notify_next_reader(loan.book)
        if notified_reservation:
            messages.info(request, f"已通知预约读者：{notified_reservation.user.username}")
        
        if loan.status == 'pending_payment':
            messages.warning(request, f"图书已归还，但存在逾期罚款 ¥{loan.fine_amount:.2f}。请提醒读者缴费。")
        else:
            messages.success(request, f"图书已成功归还。信用分{points:+d}分，当前信用分：{loan.user.credit_score}")
        
    return redirect('loan_manage')

@login_required
def confirm_payment(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    loan = get_object_or_404(LoanRecord, pk=pk)
    
    if loan.status == 'pending_payment':
        loan.status = 'returned'
        loan.fine_paid = True
        loan.payment_date = date.today()
        loan.save()
        messages.success(request, f"已确认缴费 ¥{loan.fine_amount:.2f}，借阅记录已完成。")
    
    return redirect('loan_manage')
    
@login_required
def system_settings(request):
    if request.user.role != 'admin':
        return redirect('home')
    
    config = SiteConfig.get_solo()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_config':
            config.site_title = request.POST.get('site_title')
            config.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
            daily_fine_rate = request.POST.get('daily_fine_rate', '0.5')
            try:
                config.daily_fine_rate = float(daily_fine_rate)
            except ValueError:
                config.daily_fine_rate = 0.5
            config.save()
            messages.success(request, "系统基本配置已更新。")
        elif action == 'create_announcement':
            title = request.POST.get('title')
            content = request.POST.get('content')
            Announcement.objects.create(title=title, content=content)
            messages.success(request, "公告发布成功。")
            return redirect('system_settings')
            
    announcements = Announcement.objects.all().order_by('-created_at')
    
    credit_logs = CreditLog.objects.all().select_related('user', 'operator').order_by('-created_at')[:50]
    
    return render(request, 'admin/settings.html', {
        'announcements': announcements, 
        'config': config,
        'credit_logs': credit_logs
    })

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
    
def home(request):
    check_expired_reservations()
    
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
    latest_books = Book.objects.all().order_by('-created_at')[:8]
    config = SiteConfig.get_solo()
    
    credit_ranking = User.objects.filter(role='reader', is_active=True).order_by('-credit_score')[:10]
    
    user_notifications = []
    if request.user.is_authenticated:
        user_notifications = Announcement.objects.filter(
            is_active=True,
            content__contains=request.user.username
        ).order_by('-created_at')[:3]
    
    return render(request, 'books/home.html', {
        'announcements': announcements,
        'latest_books': latest_books,
        'config': config,
        'credit_ranking': credit_ranking,
        'user_notifications': user_notifications
    })
