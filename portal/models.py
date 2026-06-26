from django.conf import settings
from django.db import models
from django.utils import timezone


class News(models.Model):
    CATEGORY_INTERNAL = 'internal'
    CATEGORY_EXTERNAL = 'external'
    CATEGORY_ANNOUNCEMENT = 'announcement'
    CATEGORY_CHOICES = [
        (CATEGORY_INTERNAL, 'ข่าวภายใน'),
        (CATEGORY_EXTERNAL, 'ข่าวภายนอก'),
        (CATEGORY_ANNOUNCEMENT, 'ประชาสัมพันธ์'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_ANNOUNCEMENT
    )
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_items',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ข่าวสาร'
        verbose_name_plural = 'ข่าวสาร'

    def __str__(self):
        return self.title


class VolunteerLink(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    external_url = models.URLField()
    organizer = models.CharField(max_length=200, blank=True, default='')
    deadline = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='volunteer_links',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'จิตอาสา'
        verbose_name_plural = 'จิตอาสา'

    def __str__(self):
        return self.title


class Competition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='competition/images/', blank=True, null=True)
    application_url = models.URLField(blank=True, null=True)
    organizer = models.CharField(max_length=200, blank=True, default='')
    deadline = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='competitions',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'การแข่งขัน'
        verbose_name_plural = 'การแข่งขัน'

    def __str__(self):
        return self.title


class StudyNote(models.Model):
    GRADE_CHOICES = [
        ('ม.1', 'ม.1'),
        ('ม.2', 'ม.2'),
        ('ม.3', 'ม.3'),
        ('ม.4', 'ม.4'),
        ('ม.5', 'ม.5'),
        ('ม.6', 'ม.6'),
    ]

    title = models.CharField(max_length=200)
    grade_level = models.CharField(max_length=20, choices=GRADE_CHOICES)
    subject = models.CharField(max_length=100)
    # TODO (Phase 3): Replace drive_url with actual Google Drive API upload integration
    drive_url = models.URLField()
    credit_name = models.CharField(max_length=150, blank=True, default='')
    is_anonymous = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='study_notes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'สรุปการเรียน'
        verbose_name_plural = 'สรุปการเรียน'

    def __str__(self):
        return f'{self.title} ({self.grade_level} - {self.subject})'

    def display_credit(self):
        if self.is_anonymous:
            return 'ไม่ระบุตัวตน'
        return self.credit_name or (self.submitted_by.full_name if self.submitted_by else 'นักเรียนสตรีวิทยา')


class ProblemReport(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'รอการอนุมัติ'),
        (STATUS_APPROVED, 'อนุมัติแล้ว'),
        (STATUS_REJECTED, 'ปฏิเสธ'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    admin_note = models.TextField(blank=True, default='')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='problem_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'รายงานปัญหา'
        verbose_name_plural = 'รายงานปัญหา'

    def __str__(self):
        return f'[{self.get_status_display()}] {self.title}'


class PointActivity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    points = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_point_activities',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'กิจกรรมสะสมแต้ม'
        verbose_name_plural = 'กิจกรรมสะสมแต้ม'

    def __str__(self):
        return f'{self.title} ({self.points} แต้ม)'


class PointSubmission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'รอตรวจสอบ'),
        (STATUS_APPROVED, 'อนุมัติแล้ว'),
        (STATUS_REJECTED, 'ไม่อนุมัติ'),
    ]

    activity = models.ForeignKey(
        PointActivity,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='กิจกรรม',
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='point_submissions',
    )
    proof_image = models.ImageField(upload_to='point_proofs/', verbose_name='ภาพหลักฐาน')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING,
        verbose_name='สถานะ',
    )
    admin_note = models.TextField(blank=True, default='', verbose_name='หมายเหตุ')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_point_submissions',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'คำขอสะสมแต้ม'
        verbose_name_plural = 'คำขอสะสมแต้ม'

    def __str__(self):
        return f'{self.submitted_by} - {self.activity.title} [{self.get_status_display()}]'


class UserPointProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='point_profile',
    )
    total_points = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'โปรไฟล์คะแนน'
        verbose_name_plural = 'โปรไฟล์คะแนน'

    def __str__(self):
        return f'{self.user} - {self.total_points} แต้ม'
