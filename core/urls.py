# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from users.forms import CustomAuthenticationForm
from . import views

app_name = 'core'

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return redirect('core:login')

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="core/login.html", authentication_form=CustomAuthenticationForm), name='login'),

    # logout با GET
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    
    # گزارشات و رهگیری هوشمند
    path('reports/', views.reports_hub, name='reports_hub'),

    # تنظیمات عمومی سامانه
    path('settings/', views.settings_view, name='settings'),

    # روت اصلی
    path('', root_redirect, name='root'),
]
