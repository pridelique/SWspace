import re

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(AuthenticationForm):
    """Accepts the full school email or just the 5-digit student ID."""

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if re.fullmatch(r'\d{5}', username):
            username += settings.STUDENT_EMAIL_DOMAIN
        return username


def _normalize_school_email(value):
    value = value.strip().lower()
    if re.fullmatch(r'\d{5}', value):
        value += settings.STUDENT_EMAIL_DOMAIN
    return value


class RegisterForm(forms.Form):
    """Committee sign-up: a student proves who they are with their roster
    credentials, and the committee code promotes that account."""

    email = forms.CharField(
        label='อีเมลโรงเรียน',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'xxxxx@satriwit.ac.th',
            'inputmode': 'email', 'autocomplete': 'username', 'autocapitalize': 'none',
        }),
    )
    password = forms.CharField(
        label='รหัสผ่าน',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'xxxxx_x.x', 'autocomplete': 'current-password',
        }),
    )
    verification_code = forms.CharField(
        max_length=50,
        label='รหัสคณะกรรมการนักเรียน',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'รหัสคณะกรรมการนักเรียน'}),
    )

    def clean_email(self):
        email = _normalize_school_email(self.cleaned_data['email'])
        if not email.endswith(settings.STUDENT_EMAIL_DOMAIN):
            raise forms.ValidationError(f'อีเมลต้องลงท้ายด้วย {settings.STUDENT_EMAIL_DOMAIN} เท่านั้น')
        return email

    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code', '').strip().upper()
        if code != settings.COMMITTEE_VERIFICATION_CODE.upper():
            raise forms.ValidationError('รหัสคณะกรรมการนักเรียนไม่ถูกต้อง')
        return code

    def clean(self):
        cleaned = super().clean()
        email, password = cleaned.get('email'), cleaned.get('password')
        if email and password and 'verification_code' in cleaned:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError('อีเมลหรือรหัสผ่านไม่ถูกต้อง')
        return cleaned
