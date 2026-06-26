from django import forms

from .models import Competition, News, PointActivity, PointSubmission, ProblemReport, StudyNote, VolunteerLink


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'description', 'category', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หัวข้อข่าวสาร'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียด'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'หัวข้อข่าวสาร',
            'description': 'รายละเอียด',
            'category': 'หมวดหมู่',
            'image': 'รูปภาพประกอบ',
            'is_published': 'เผยแพร่ทันที',
        }


class VolunteerLinkForm(forms.ModelForm):
    class Meta:
        model = VolunteerLink
        fields = ['title', 'description', 'external_url', 'organizer', 'deadline', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อกิจกรรมจิตอาสา'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียดกิจกรรม'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อองค์กรหรือผู้จัด'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'ชื่อกิจกรรม',
            'description': 'รายละเอียด',
            'external_url': 'ลิงก์กิจกรรม',
            'organizer': 'ผู้จัด / องค์กร',
            'deadline': 'วันปิดรับสมัคร',
            'is_published': 'เผยแพร่ทันที',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ทำให้ DateInput แสดงค่าในรูปแบบ YYYY-MM-DD เสมอ เพื่อให้ input type=date ทำงานถูกต้อง
        self.fields['deadline'].input_formats = ['%Y-%m-%d']


class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'image', 'application_url', 'organizer', 'deadline', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อการแข่งขัน'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียดการแข่งขัน'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'application_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'organizer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อองค์กรหรือผู้จัด'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'ชื่อการแข่งขัน',
            'description': 'รายละเอียด',
            'image': 'รูปภาพประกอบ',
            'application_url': 'ลิงก์สมัคร / รายละเอียด',
            'organizer': 'ผู้จัด / องค์กร',
            'deadline': 'วันปิดรับสมัคร',
            'is_published': 'เผยแพร่ทันที',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].input_formats = ['%Y-%m-%d']


class StudyNoteForm(forms.ModelForm):
    class Meta:
        model = StudyNote
        fields = ['title', 'grade_level', 'subject', 'drive_url', 'credit_name', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อสรุป เช่น สรุปฟิสิกส์บท 3'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น คณิตศาสตร์, ฟิสิกส์'}),
            'drive_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/...'}),
            'credit_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อที่ต้องการให้แสดง (ถ้าเว้นว่างจะใช้ชื่อบัญชี)'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'ชื่อสรุป',
            'grade_level': 'ระดับชั้น',
            'subject': 'วิชา',
            'drive_url': 'ลิงก์ Google Drive',
            'credit_name': 'ชื่อที่ต้องการแสดงเครดิต (ไม่บังคับ)',
            'is_anonymous': 'ไม่ระบุตัวตน',
        }

    def clean_drive_url(self):
        url = self.cleaned_data.get('drive_url', '')
        if url and 'google' not in url.lower():
            raise forms.ValidationError('กรุณาใส่ลิงก์ Google Drive หรือ Google Docs เท่านั้น')
        return url


class ProblemReportForm(forms.ModelForm):
    class Meta:
        model = ProblemReport
        fields = ['title', 'description', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'หัวข้อปัญหา'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'อธิบายปัญหาให้ชัดเจน อย่างน้อย 10 ตัวอักษร'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น อาคาร 3 ชั้น 2, ห้องน้ำข้างโรงอาหาร'}),
        }
        labels = {
            'title': 'หัวข้อปัญหา',
            'description': 'รายละเอียดปัญหา',
            'location': 'สถานที่ (ไม่บังคับ)',
        }

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if len(desc) < 10:
            raise forms.ValidationError('กรุณาอธิบายปัญหาอย่างน้อย 10 ตัวอักษร')
        return desc


class PointActivityForm(forms.ModelForm):
    class Meta:
        model = PointActivity
        fields = ['title', 'description', 'points', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อกิจกรรม'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'รายละเอียด (ถ้ามี)'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'ชื่อกิจกรรม',
            'description': 'รายละเอียด',
            'points': 'คะแนนที่ได้รับ',
            'is_active': 'เปิดรับหลักฐาน',
        }

    def clean_points(self):
        points = self.cleaned_data.get('points')
        if points is not None and points <= 0:
            raise forms.ValidationError('คะแนนต้องมากกว่า 0')
        return points


class PointSubmissionForm(forms.ModelForm):
    class Meta:
        model = PointSubmission
        fields = ['activity', 'proof_image']
        widgets = {
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'proof_image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/webp',
            }),
        }
        labels = {
            'activity': 'กิจกรรมที่ต้องการสะสมแต้ม',
            'proof_image': 'ภาพหลักฐาน',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['activity'].queryset = PointActivity.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        activity = cleaned_data.get('activity')
        if activity and self.user:
            existing = (
                PointSubmission.objects
                .filter(submitted_by=self.user, activity=activity)
                .order_by('-created_at')
                .first()
            )
            if existing:
                if existing.status == PointSubmission.STATUS_APPROVED:
                    raise forms.ValidationError('คุณได้รับคะแนนจากกิจกรรมนี้แล้ว ไม่สามารถส่งซ้ำได้')
                if existing.status == PointSubmission.STATUS_PENDING:
                    raise forms.ValidationError('คุณส่งหลักฐานกิจกรรมนี้แล้ว กรุณารอการตรวจสอบ')
        return cleaned_data

    def clean_proof_image(self):
        f = self.cleaned_data.get('proof_image')
        if f:
            allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
            if hasattr(f, 'content_type') and f.content_type not in allowed_types:
                raise forms.ValidationError('รองรับเฉพาะ JPG, PNG, WEBP เท่านั้น')
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError('ไฟล์ใหญ่เกิน 5 MB กรุณาบีบอัดรูปก่อนอัปโหลด')
        return f


class PointRejectForm(forms.Form):
    admin_note = forms.CharField(
        required=False,
        label='หมายเหตุ (ไม่บังคับ)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'เหตุผลที่ปฏิเสธ...',
        }),
    )
