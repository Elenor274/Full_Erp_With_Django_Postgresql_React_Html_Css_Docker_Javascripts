from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from .models import UserProfile
from .forms import UserForm, UserEditForm, UserProfileForm, PasswordChangeCustomForm

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().select_related('userprofile')
    return render(request, 'users/user_list.html', {'users_list': users})

@login_required
@admin_required
def user_create(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # Since UserProfile is created automatically on post_save, retrieve it and update
            profile = user.userprofile
            for field_name, value in profile_form.cleaned_data.items():
                setattr(profile, field_name, value)
            profile.save()
            
            messages.success(request, f"کاربر {user.username} با موفقیت ساخته شد.")
            return redirect('users:user_list')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'users/user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'ایجاد کاربر جدید'
    })

@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    # Ensure profile exists
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f"کاربر {user.username} با موفقیت ویرایش شد.")
            return redirect('users:user_list')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
        
    return render(request, 'users/user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': f'ویرایش کاربر: {user.username}'
    })

@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "شما نمی‌توانید حساب کاربری خودتان را حذف کنید.")
        return redirect('users:user_list')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"کاربر {user.username} حذف شد.")
        return redirect('users:user_list')
        
    return render(request, 'users/user_confirm_delete.html', {'user_to_delete': user})

@login_required
@admin_required
def user_change_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, f"رمز عبور کاربر {user.username} با موفقیت تغییر کرد.")
            return redirect('users:user_list')
    else:
        form = PasswordChangeCustomForm()
    return render(request, 'users/user_change_password.html', {'form': form, 'user': user})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    info_form = UserEditForm(instance=request.user)
    password_form = PasswordChangeCustomForm()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_info':
            info_form = UserEditForm(request.POST, instance=request.user)
            if info_form.is_valid():
                info_form.save()
                messages.success(request, "اطلاعات کاربری شما با موفقیت بروزرسانی شد.")
                return redirect('users:profile')
        elif action == 'change_password':
            password_form = PasswordChangeCustomForm(request.POST)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                messages.success(request, "رمز عبور شما با موفقیت تغییر کرد.")
                return redirect('users:profile')
                
    return render(request, 'users/profile.html', {
        'profile': profile,
        'info_form': info_form,
        'password_form': password_form,
    })
