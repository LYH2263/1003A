from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/chart-data/', views.dashboard_chart_data, name='dashboard_chart_data'),
    
    # Book Management
    path('books/manage/', views.book_manage, name='book_manage'),
    path('books/create/', views.book_create, name='book_create'), # Added
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'), # Added
    path('books/browse/', views.book_browse, name='book_browse'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/borrow/', views.borrow_request, name='borrow_request'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # Review System
    path('books/<int:pk>/review/', views.review_create, name='review_create'),
    path('reviews/<int:review_pk>/reply/', views.review_reply_create, name='review_reply_create'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('reviews/manage/', views.review_manage, name='review_manage'),
    
    # Reservation System
    path('books/<int:pk>/reserve/', views.join_reservation, name='join_reservation'),
    path('reservations/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('books/<int:pk>/reservations/', views.reservation_queue, name='reservation_queue'),
    path('reservations/<int:pk>/remove/', views.remove_reservation, name='remove_reservation'),
    
    # Loan Management
    path('my-loans/', views.my_loans, name='my_loans'),
    path('loans/<int:pk>/renew/', views.renew_loan, name='renew_loan'),
    path('users/manage/', views.user_manage, name='user_manage'),
    path('loans/manage/', views.loan_manage, name='loan_manage'),
    path('loans/<int:pk>/audit/<str:action>/', views.audit_loan, name='audit_loan'),
    path('loans/<int:pk>/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/announcements/create/', views.announcement_create, name='announcement_create'),
    path('settings/announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    
    # Book List / Favorites System
    path('books/<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('books/<int:pk>/check-favorite/', views.check_favorite, name='check_favorite'),
    path('my-book-lists/', views.my_book_lists, name='my_book_lists'),
    path('book-lists/create/', views.book_list_create, name='book_list_create'),
    path('book-lists/<int:pk>/edit/', views.book_list_edit, name='book_list_edit'),
    path('book-lists/<int:pk>/delete/', views.book_list_delete, name='book_list_delete'),
    path('book-lists/<int:list_pk>/add/<int:book_pk>/', views.book_list_add_book, name='book_list_add_book'),
    path('book-lists/<int:list_pk>/remove/<int:book_pk>/', views.book_list_remove_book, name='book_list_remove_book'),
    path('book-lists/<int:pk>/share/', views.book_list_share, name='book_list_share'),
    path('shared-list/<str:token>/', views.shared_book_list, name='shared_book_list'),
]
