from django.urls import path
from . import views

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/reply/', views.create_reply, name='create_reply'),
    path('post/<int:post_id>/pin/', views.toggle_pin_post, name='toggle_pin_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
]
