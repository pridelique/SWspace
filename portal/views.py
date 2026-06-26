from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    CompetitionForm, NewsForm, PointActivityForm, PointRejectForm,
    PointSubmissionForm, ProblemReportForm, StudyNoteForm, VolunteerLinkForm,
)
from .models import (
    Competition, News, PointActivity, PointSubmission,
    ProblemReport, StudyNote, UserPointProfile, VolunteerLink,
)


def committee_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        if not request.user.is_committee():
            messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
            return redirect('portal:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Public views ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    return render(request, 'portal/dashboard.html')


@login_required
def news(request):
    items = News.objects.filter(is_published=True).select_related('created_by')
    return render(request, 'portal/news.html', {'items': items})


@login_required
def volunteer(request):
    items = VolunteerLink.objects.filter(is_published=True).select_related('created_by')
    return render(request, 'portal/volunteer.html', {'items': items})


@login_required
def competitions(request):
    items = Competition.objects.filter(is_published=True).select_related('created_by')
    return render(request, 'portal/competitions.html', {'items': items})


@login_required
def study_notes(request):
    items = StudyNote.objects.filter(is_approved=True).select_related('submitted_by')
    return render(request, 'portal/study_notes.html', {'items': items})


@login_required
def problem_reports(request):
    approved = ProblemReport.objects.filter(
        status=ProblemReport.STATUS_APPROVED
    ).select_related('submitted_by')
    return render(request, 'portal/problem_reports.html', {'approved': approved})


# ─── Committee Dashboard ─────────────────────────────────────────────────────

@login_required
def committee_dashboard(request):
    if not request.user.is_committee():
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
        return redirect('portal:dashboard')

    stats = {
        'news_count': News.objects.count(),
        'volunteer_count': VolunteerLink.objects.count(),
        'competition_count': Competition.objects.count(),
        'study_note_count': StudyNote.objects.count(),
        'problem_pending_count': ProblemReport.objects.filter(status=ProblemReport.STATUS_PENDING).count(),
        'problem_approved_count': ProblemReport.objects.filter(status=ProblemReport.STATUS_APPROVED).count(),
        'problem_rejected_count': ProblemReport.objects.filter(status=ProblemReport.STATUS_REJECTED).count(),
        'point_pending_count': PointSubmission.objects.filter(status=PointSubmission.STATUS_PENDING).count(),
        'point_activity_count': PointActivity.objects.filter(is_active=True).count(),
    }
    return render(request, 'portal/committee.html', {'stats': stats})


# ─── News CRUD ────────────────────────────────────────────────────────────────

@committee_required
def committee_news_list(request):
    items = News.objects.all().select_related('created_by')
    return render(request, 'portal/committee_news_list.html', {'items': items})


@committee_required
def committee_news_create(request):
    form = NewsForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.created_by = request.user
        item.save()
        messages.success(request, f'เพิ่มข่าวสาร "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_news_list')
    return render(request, 'portal/committee_news_form.html', {
        'form': form,
        'action': 'เพิ่มข่าวสาร',
    })


@committee_required
def committee_news_edit(request, pk):
    item = get_object_or_404(News, pk=pk)
    form = NewsForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'แก้ไขข่าวสาร "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_news_list')
    return render(request, 'portal/committee_news_form.html', {
        'form': form,
        'item': item,
        'action': 'แก้ไขข่าวสาร',
    })


@committee_required
def committee_news_delete(request, pk):
    item = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'ลบข่าวสาร "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_news_list')
    return render(request, 'portal/committee_news_confirm_delete.html', {'item': item})


# ─── VolunteerLink CRUD ──────────────────────────────────────────────────────

@committee_required
def committee_volunteer_list(request):
    items = VolunteerLink.objects.all().select_related('created_by')
    return render(request, 'portal/committee_volunteer_list.html', {'items': items})


@committee_required
def committee_volunteer_create(request):
    form = VolunteerLinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.created_by = request.user
        item.save()
        messages.success(request, f'เพิ่มกิจกรรมจิตอาสา "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_volunteer_list')
    return render(request, 'portal/committee_volunteer_form.html', {
        'form': form,
        'action': 'เพิ่มกิจกรรมจิตอาสา',
    })


@committee_required
def committee_volunteer_edit(request, pk):
    item = get_object_or_404(VolunteerLink, pk=pk)
    form = VolunteerLinkForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'แก้ไขกิจกรรมจิตอาสา "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_volunteer_list')
    return render(request, 'portal/committee_volunteer_form.html', {
        'form': form,
        'item': item,
        'action': 'แก้ไขกิจกรรมจิตอาสา',
    })


@committee_required
def committee_volunteer_delete(request, pk):
    item = get_object_or_404(VolunteerLink, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'ลบกิจกรรมจิตอาสา "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_volunteer_list')
    return render(request, 'portal/committee_volunteer_confirm_delete.html', {'item': item})


# ─── Competition CRUD ─────────────────────────────────────────────────────────

@committee_required
def committee_competition_list(request):
    items = Competition.objects.all().select_related('created_by')
    return render(request, 'portal/committee_competition_list.html', {'items': items})


@committee_required
def committee_competition_create(request):
    form = CompetitionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.created_by = request.user
        item.save()
        messages.success(request, f'เพิ่มการแข่งขัน "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_competition_list')
    return render(request, 'portal/committee_competition_form.html', {
        'form': form,
        'action': 'เพิ่มการแข่งขัน',
    })


@committee_required
def committee_competition_edit(request, pk):
    item = get_object_or_404(Competition, pk=pk)
    form = CompetitionForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'แก้ไขการแข่งขัน "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_competition_list')
    return render(request, 'portal/committee_competition_form.html', {
        'form': form,
        'item': item,
        'action': 'แก้ไขการแข่งขัน',
    })


@committee_required
def committee_competition_delete(request, pk):
    item = get_object_or_404(Competition, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'ลบการแข่งขัน "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_competition_list')
    return render(request, 'portal/committee_competition_confirm_delete.html', {'item': item})


# ─── Study Notes ─────────────────────────────────────────────────────────────

@login_required
def study_note_submit(request):
    form = StudyNoteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.submitted_by = request.user
        item.is_approved = True
        item.save()
        messages.success(request, f'ส่งสรุป "{item.title}" เรียบร้อยแล้ว ขอบคุณที่แบ่งปัน!')
        return redirect('portal:study_notes')
    return render(request, 'portal/study_note_form.html', {'form': form})


@committee_required
def committee_study_notes_list(request):
    items = StudyNote.objects.all().select_related('submitted_by').order_by('-created_at')
    return render(request, 'portal/committee_study_notes_list.html', {'items': items})


@committee_required
def committee_study_note_toggle_approval(request, pk):
    if request.method != 'POST':
        return redirect('portal:committee_study_notes')
    item = get_object_or_404(StudyNote, pk=pk)
    item.is_approved = not item.is_approved
    item.save()
    state = 'อนุมัติ' if item.is_approved else 'ซ่อน'
    messages.success(request, f'{state}สรุป "{item.title}" เรียบร้อยแล้ว')
    return redirect('portal:committee_study_notes')


@committee_required
def committee_study_note_delete(request, pk):
    item = get_object_or_404(StudyNote, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'ลบสรุป "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_study_notes')
    return render(request, 'portal/committee_study_note_confirm_delete.html', {'item': item})


# ─── Problem Reports ──────────────────────────────────────────────────────────

@login_required
def problem_report_submit(request):
    form = ProblemReportForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.submitted_by = request.user
        item.status = ProblemReport.STATUS_PENDING
        item.save()
        messages.success(request, f'ส่งแจ้งปัญหา "{item.title}" เรียบร้อยแล้ว กรุณารอคณะกรรมการนักเรียนตรวจสอบ')
        return redirect('portal:problem_reports')
    return render(request, 'portal/problem_report_form.html', {'form': form})


@committee_required
def committee_problem_reports_list(request):
    status_filter = request.GET.get('status', '')
    items = ProblemReport.objects.all().select_related('submitted_by').order_by('-created_at')
    if status_filter in [ProblemReport.STATUS_PENDING, ProblemReport.STATUS_APPROVED, ProblemReport.STATUS_REJECTED]:
        items = items.filter(status=status_filter)
    return render(request, 'portal/committee_problem_reports_list.html', {
        'items': items,
        'status_filter': status_filter,
        'STATUS_PENDING': ProblemReport.STATUS_PENDING,
        'STATUS_APPROVED': ProblemReport.STATUS_APPROVED,
        'STATUS_REJECTED': ProblemReport.STATUS_REJECTED,
    })


@committee_required
def committee_problem_report_approve(request, pk):
    if request.method != 'POST':
        return redirect('portal:committee_problem_reports')
    item = get_object_or_404(ProblemReport, pk=pk)
    item.status = ProblemReport.STATUS_APPROVED
    item.save()
    messages.success(request, f'อนุมัติปัญหา "{item.title}" เรียบร้อยแล้ว')
    return redirect('portal:committee_problem_reports')


@committee_required
def committee_problem_report_reject(request, pk):
    item = get_object_or_404(ProblemReport, pk=pk)
    if request.method == 'POST':
        item.status = ProblemReport.STATUS_REJECTED
        admin_note = request.POST.get('admin_note', '').strip()
        if admin_note:
            item.admin_note = admin_note
        item.save()
        messages.success(request, f'ปฏิเสธปัญหา "{item.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_problem_reports')
    return render(request, 'portal/committee_problem_report_reject_form.html', {'item': item})


@committee_required
def committee_problem_report_delete(request, pk):
    item = get_object_or_404(ProblemReport, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'ลบการแจ้งปัญหา "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_problem_reports')
    return render(request, 'portal/committee_problem_report_confirm_delete.html', {'item': item})


# ─── Points (user) ────────────────────────────────────────────────────────────

@login_required
def points(request):
    profile, _ = UserPointProfile.objects.get_or_create(user=request.user)
    activities = PointActivity.objects.filter(is_active=True)

    user_subs = (
        PointSubmission.objects
        .filter(submitted_by=request.user, activity__in=activities)
        .select_related('activity')
        .order_by('-created_at')
    )
    latest_by_activity = {}
    for sub in user_subs:
        if sub.activity_id not in latest_by_activity:
            latest_by_activity[sub.activity_id] = sub

    activity_items = [
        {'activity': a, 'latest': latest_by_activity.get(a.pk)}
        for a in activities
    ]

    return render(request, 'portal/points.html', {
        'profile': profile,
        'activity_items': activity_items,
    })


@login_required
def point_submit(request):
    initial = {}
    activity_id = request.GET.get('activity')
    if activity_id:
        initial['activity'] = activity_id
    if request.method == 'POST':
        form = PointSubmissionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.submitted_by = request.user
            submission.status = PointSubmission.STATUS_PENDING
            submission.save()
            messages.success(request, 'ส่งหลักฐานสะสมแต้มสำเร็จ กรุณารอคณะกรรมการตรวจสอบ')
            return redirect('portal:points')
    else:
        form = PointSubmissionForm(initial=initial, user=request.user)
    return render(request, 'portal/point_submit.html', {'form': form})


@login_required
def point_history(request):
    submissions = (
        PointSubmission.objects
        .filter(submitted_by=request.user)
        .select_related('activity')
        .order_by('-created_at')
    )
    return render(request, 'portal/point_history.html', {'submissions': submissions})


# ─── Points (committee) ───────────────────────────────────────────────────────

@committee_required
def committee_points(request):
    activities = PointActivity.objects.all().select_related('created_by')
    status_filter = request.GET.get('status', '')
    submissions = (
        PointSubmission.objects
        .all()
        .select_related('activity', 'submitted_by', 'approved_by')
        .order_by('-created_at')
    )
    if status_filter in [PointSubmission.STATUS_PENDING, PointSubmission.STATUS_APPROVED, PointSubmission.STATUS_REJECTED]:
        submissions = submissions.filter(status=status_filter)
    return render(request, 'portal/committee_points.html', {
        'activities': activities,
        'submissions': submissions,
        'status_filter': status_filter,
        'STATUS_PENDING': PointSubmission.STATUS_PENDING,
        'STATUS_APPROVED': PointSubmission.STATUS_APPROVED,
        'STATUS_REJECTED': PointSubmission.STATUS_REJECTED,
    })


@committee_required
def committee_point_activity_create(request):
    form = PointActivityForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        activity = form.save(commit=False)
        activity.created_by = request.user
        activity.save()
        messages.success(request, f'เพิ่มกิจกรรม "{activity.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_points')
    return render(request, 'portal/committee_point_activity_form.html', {
        'form': form,
        'action': 'เพิ่มกิจกรรม',
    })


@committee_required
def committee_point_activity_edit(request, pk):
    activity = get_object_or_404(PointActivity, pk=pk)
    form = PointActivityForm(request.POST or None, instance=activity)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'แก้ไขกิจกรรม "{activity.title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_points')
    return render(request, 'portal/committee_point_activity_form.html', {
        'form': form,
        'activity': activity,
        'action': 'แก้ไขกิจกรรม',
    })


@committee_required
def committee_point_activity_delete(request, pk):
    activity = get_object_or_404(PointActivity, pk=pk)
    if request.method == 'POST':
        title = activity.title
        activity.delete()
        messages.success(request, f'ลบกิจกรรม "{title}" เรียบร้อยแล้ว')
        return redirect('portal:committee_points')
    return render(request, 'portal/committee_point_activity_confirm_delete.html', {'activity': activity})


@committee_required
def committee_point_submission_approve(request, pk):
    if request.method != 'POST':
        return redirect('portal:committee_points')
    submission = get_object_or_404(PointSubmission, pk=pk)
    if submission.status == PointSubmission.STATUS_APPROVED:
        messages.warning(request, 'รายการนี้ถูกอนุมัติไปแล้ว คะแนนจึงไม่ถูกเพิ่มซ้ำ')
        return redirect('portal:committee_points')
    with transaction.atomic():
        submission.status = PointSubmission.STATUS_APPROVED
        submission.approved_by = request.user
        submission.approved_at = timezone.now()
        submission.save()
        profile, _ = UserPointProfile.objects.get_or_create(user=submission.submitted_by)
        UserPointProfile.objects.filter(pk=profile.pk).update(
            total_points=F('total_points') + submission.activity.points
        )
    messages.success(
        request,
        f'อนุมัติและเพิ่ม {submission.activity.points} แต้มให้ {submission.submitted_by.full_name} เรียบร้อยแล้ว',
    )
    return redirect('portal:committee_points')


@committee_required
def committee_point_submission_reject(request, pk):
    submission = get_object_or_404(PointSubmission, pk=pk)
    if submission.status == PointSubmission.STATUS_APPROVED:
        messages.error(request, 'รายการนี้อนุมัติแล้ว ไม่สามารถปฏิเสธย้อนหลังได้')
        return redirect('portal:committee_points')
    form = PointRejectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        submission.status = PointSubmission.STATUS_REJECTED
        submission.admin_note = form.cleaned_data.get('admin_note', '')
        submission.save()
        messages.success(request, 'ปฏิเสธรายการสะสมแต้มเรียบร้อยแล้ว')
        return redirect('portal:committee_points')
    return render(request, 'portal/committee_point_submission_reject_form.html', {
        'form': form,
        'submission': submission,
    })


@committee_required
def committee_point_submission_delete(request, pk):
    submission = get_object_or_404(PointSubmission, pk=pk)
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'ลบรายการส่งหลักฐานเรียบร้อยแล้ว')
        return redirect('portal:committee_points')
    return render(request, 'portal/committee_point_submission_confirm_delete.html', {'submission': submission})
