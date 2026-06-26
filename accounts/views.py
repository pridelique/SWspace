from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import RegisterForm

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        role = form.determine_role()
        grade_level = form.determine_grade_level()
        user = User.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
            full_name=form.cleaned_data['full_name'],
            role=role,
            verification_code=form.cleaned_data['verification_code'],
            grade_level=grade_level,
        )
        auth.login(request, user)
        messages.success(request, f'สมัครสมาชิกสำเร็จ ยินดีต้อนรับ {user.full_name}')
        return redirect('portal:dashboard')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        auth.login(request, user)
        messages.success(request, f'เข้าสู่ระบบสำเร็จ ยินดีต้อนรับ {user.full_name}')
        next_url = request.GET.get('next', 'portal:dashboard')
        return redirect(next_url)
    elif request.method == 'POST':
        messages.error(request, 'อีเมลหรือรหัสผ่านไม่ถูกต้อง')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, 'ออกจากระบบแล้ว')
        return redirect('accounts:login')
    return redirect('portal:dashboard')
