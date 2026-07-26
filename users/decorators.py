from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        try:
            profile = getattr(request.user, 'userprofile', None)
            if profile and profile.is_admin_user:
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
        messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
        return redirect('core:dashboard')
    return _wrapped_view

def permission_required_custom(permission_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            try:
                profile = getattr(request.user, 'userprofile', None)
                if profile:
                    if profile.is_admin_user:
                        return view_func(request, *args, **kwargs)
                    if permission_name.startswith('access_production_') and profile.access_production:
                        return view_func(request, *args, **kwargs)
                    if getattr(profile, permission_name, False):
                        return view_func(request, *args, **kwargs)
            except Exception:
                pass
            messages.error(request, "شما دسترسی لازم برای این قسمت را ندارید.")
            return redirect('core:dashboard')
        return _wrapped_view
    return decorator
