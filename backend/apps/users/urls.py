from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('<int:pk>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
]
