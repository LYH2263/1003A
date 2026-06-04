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
    
    # Loan Management
    path('my-loans/', views.my_loans, name='my_loans'),
    path('users/manage/', views.user_manage, name='user_manage'),
    path('loans/manage/', views.loan_manage, name='loan_manage'),
    path('loans/<int:pk>/audit/<str:action>/', views.audit_loan, name='audit_loan'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/announcements/create/', views.announcement_create, name='announcement_create'),
    path('settings/announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
]
