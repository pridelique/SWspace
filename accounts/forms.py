from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

STUDENT_CODE_GRADE_MAP = {
    'SW127': 'ม.1',
    'SW126': 'ม.2',
    'SW125': 'ม.3',
    'SW124': 'ม.4',
    'SW123': 'ม.5',
    'SW122': 'ม.6',
}


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        label='ชื่อ-นามสกุล',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อ-นามสกุล'}),
    )
    email = forms.EmailField(
        label='อีเมล',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@satriwit.ac.th'}),
    )
    password = forms.CharField(
        label='รหัสผ่าน',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'รหัสผ่าน'}),
    )
    confirm_password = forms.CharField(
        label='ยืนยันรหัสผ่าน',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ยืนยันรหัสผ่าน'}),
    )
    verification_code = forms.CharField(
        max_length=50,
        label='รหัสยืนยัน',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'รหัสยืนยันตัวตน'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        domain = settings.STUDENT_EMAIL_DOMAIN
        if not email.endswith(domain):
            raise forms.ValidationError(f'อีเมลต้องลงท้ายด้วย {domain} เท่านั้น')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('อีเมลนี้ถูกใช้งานแล้ว')
        return email

    def clean_verification_code(self):
        code = self.cleaned_data.get('verification_code', '').strip().upper()
        if code == settings.COMMITTEE_VERIFICATION_CODE:
            return code
        if code in STUDENT_CODE_GRADE_MAP:
            return code
        raise forms.ValidationError('รหัสยืนยันตัวตนไม่ถูกต้อง')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'รหัสผ่านไม่ตรงกัน')
        return cleaned_data

    def determine_role(self):
        code = self.cleaned_data.get('verification_code', '')
        if code == settings.COMMITTEE_VERIFICATION_CODE:
            return 'committee'
        return 'student'

    def determine_grade_level(self):
        code = self.cleaned_data.get('verification_code', '')
        return STUDENT_CODE_GRADE_MAP.get(code, '')
