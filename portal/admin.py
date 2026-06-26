from django.contrib import admin

from .models import (
    Competition, News, PointActivity, PointSubmission,
    ProblemReport, StudyNote, UserPointProfile, VolunteerLink,
)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_by', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'description', 'image')}),
        ('การจัดหมวดหมู่', {'fields': ('category', 'is_published')}),
        ('ข้อมูลระบบ', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(VolunteerLink)
class VolunteerLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'deadline', 'is_published', 'created_by', 'created_at']
    list_filter = ['is_published', 'deadline']
    search_fields = ['title', 'description', 'organizer']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'description', 'external_url')}),
        ('รายละเอียด', {'fields': ('organizer', 'deadline', 'is_published')}),
        ('ข้อมูลระบบ', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'deadline', 'is_published', 'created_by', 'created_at']
    list_filter = ['is_published', 'deadline']
    search_fields = ['title', 'description', 'organizer']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_published']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'description', 'image')}),
        ('รายละเอียด', {'fields': ('organizer', 'deadline', 'application_url', 'is_published')}),
        ('ข้อมูลระบบ', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(StudyNote)
class StudyNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'grade_level', 'subject', 'is_approved', 'is_anonymous', 'submitted_by', 'created_at']
    list_filter = ['grade_level', 'subject', 'is_approved', 'is_anonymous']
    search_fields = ['title', 'subject', 'credit_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_approved']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'grade_level', 'subject', 'drive_url')}),
        ('เครดิต', {'fields': ('credit_name', 'is_anonymous')}),
        ('สถานะ', {'fields': ('is_approved',)}),
        ('ข้อมูลระบบ', {'fields': ('submitted_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(ProblemReport)
class ProblemReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'status', 'submitted_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'description', 'location')}),
        ('การดำเนินการ', {'fields': ('status', 'admin_note')}),
        ('ข้อมูลระบบ', {'fields': ('submitted_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(PointActivity)
class PointActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'points', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
    fieldsets = (
        ('เนื้อหา', {'fields': ('title', 'description', 'points', 'is_active')}),
        ('ข้อมูลระบบ', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(PointSubmission)
class PointSubmissionAdmin(admin.ModelAdmin):
    list_display = ['activity', 'submitted_by', 'status', 'approved_by', 'created_at']
    list_filter = ['status', 'activity', 'created_at']
    search_fields = ['submitted_by__email', 'submitted_by__full_name', 'activity__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    fieldsets = (
        ('ข้อมูล', {'fields': ('activity', 'submitted_by', 'proof_image')}),
        ('การดำเนินการ', {'fields': ('status', 'admin_note', 'approved_by', 'approved_at')}),
        ('ข้อมูลระบบ', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(UserPointProfile)
class UserPointProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'updated_at']
    search_fields = ['user__email', 'user__full_name']
    readonly_fields = ['updated_at']
