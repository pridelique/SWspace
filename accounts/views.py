from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.user
        user.role = User.ROLE_COMMITTEE
        user.verification_code = form.cleaned_data['verification_code']
        user.save(update_fields=['role', 'verification_code'])
        auth.login(request, user)
        messages.success(request, f'ลงทะเบียนคณะกรรมการสำเร็จ ยินดีต้อนรับ {user.full_name}')
        return redirect('portal:dashboard')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        messages.success(request, f'เข้าสู่ระบบสำเร็จ ยินดีต้อนรับ {user.full_name}')
        next_url = request.GET.get('next', '')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('portal:dashboard')
    elif request.method == 'POST':
        messages.error(request, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, 'ออกจากระบบแล้ว')
        return redirect('accounts:login')
    return redirect('portal:dashboard')
