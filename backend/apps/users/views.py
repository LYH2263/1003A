from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role', 'reader')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role != role:
                messages.error(request, f"身份不匹配。该账户不是{ '管理员' if role == 'admin' else '普通读者' }。")
            else:
                login(request, user)
                messages.success(request, f"欢迎回来，{user.username}！")
                return redirect('home')
        else:
            # Check if user exists but is disabled
            try:
                exist_user = User.objects.get(username=username)
                if not exist_user.is_active and exist_user.check_password(password):
                    messages.error(request, "账户已被禁用，请联系管理员。")
                else:
                    messages.error(request, "用户名或密码错误。")
            except User.DoesNotExist:
                messages.error(request, "用户名或密码错误。")
            
    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "用户名已存在。")
        elif password != password_confirm:
            messages.error(request, "两次输入的密码不一致。")
        else:
            User.objects.create_user(
                username=username,
                phone=phone,
                password=password,
                role='reader'
            )
            messages.success(request, "注册成功，请登录！")
            return redirect('login')
            
    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "您已成功退出登录。")
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            phone = request.POST.get('phone')
            request.user.phone = phone
            request.user.save()
            messages.success(request, "个人信息已更新。")
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(old_password):
                messages.error(request, "原密码错误。")
            elif new_password != confirm_password:
                messages.error(request, "两次输入的新密码不一致。")
            else:
                request.user.set_password(new_password)
                request.user.save()
                login(request, request.user) # Keep user logged in
                messages.success(request, "密码修改成功。")
        return redirect('profile')
        
    return render(request, 'auth/profile.html')

@login_required
def user_toggle_status(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser or user == request.user:
        messages.error(request, "无法更改管理员或自己的状态。")
    else:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f"用户 {user.username} 状态已更新为 {'活跃' if user.is_active else '禁用'}。")
    return redirect('user_manage')

@login_required
def user_edit(request, pk):
    if request.user.role != 'admin':
        return redirect('home')
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        
        user.phone = phone
        if not user.is_superuser and user != request.user:
             user.role = role
        
        user.save()
        messages.success(request, f"用户 {user.username} 信息已更新。")
        return redirect('user_manage')
        
    # Ideally should render a separate template or use a modal, 
    # but for simplicity we might just redirect or handle it via a modal on the list page.
    # Here assuming a separate simple edit page or returning to list if handled by modal logic.
    return redirect('user_manage') 
