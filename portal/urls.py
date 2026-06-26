from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    # ── Public ──────────────────────────────────────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),
    path('news/', views.news, name='news'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('competitions/', views.competitions, name='competitions'),
    path('study-notes/', views.study_notes, name='study_notes'),
    path('problem-reports/', views.problem_reports, name='problem_reports'),

    # ── Committee Dashboard ─────────────────────────────────────────────────
    path('committee/', views.committee_dashboard, name='committee'),

    # ── News CRUD (committee only) ──────────────────────────────────────────
    path('committee/news/', views.committee_news_list, name='committee_news_list'),
    path('committee/news/create/', views.committee_news_create, name='committee_news_create'),
    path('committee/news/<int:pk>/edit/', views.committee_news_edit, name='committee_news_edit'),
    path('committee/news/<int:pk>/delete/', views.committee_news_delete, name='committee_news_delete'),

    # ── VolunteerLink CRUD (committee only) ────────────────────────────────
    path('committee/volunteer/', views.committee_volunteer_list, name='committee_volunteer_list'),
    path('committee/volunteer/create/', views.committee_volunteer_create, name='committee_volunteer_create'),
    path('committee/volunteer/<int:pk>/edit/', views.committee_volunteer_edit, name='committee_volunteer_edit'),
    path('committee/volunteer/<int:pk>/delete/', views.committee_volunteer_delete, name='committee_volunteer_delete'),

    # ── Competition CRUD (committee only) ──────────────────────────────────
    path('committee/competitions/', views.committee_competition_list, name='committee_competition_list'),
    path('committee/competitions/create/', views.committee_competition_create, name='committee_competition_create'),
    path('committee/competitions/<int:pk>/edit/', views.committee_competition_edit, name='committee_competition_edit'),
    path('committee/competitions/<int:pk>/delete/', views.committee_competition_delete, name='committee_competition_delete'),

    # ── Study Notes ─────────────────────────────────────────────────────────
    path('study-notes/submit/', views.study_note_submit, name='study_note_submit'),
    path('committee/study-notes/', views.committee_study_notes_list, name='committee_study_notes'),
    path('committee/study-notes/<int:pk>/toggle-approval/', views.committee_study_note_toggle_approval, name='committee_study_note_toggle_approval'),
    path('committee/study-notes/<int:pk>/delete/', views.committee_study_note_delete, name='committee_study_note_delete'),

    # ── Problem Reports ─────────────────────────────────────────────────────
    path('problem-reports/submit/', views.problem_report_submit, name='problem_report_submit'),
    path('committee/problem-reports/', views.committee_problem_reports_list, name='committee_problem_reports'),
    path('committee/problem-reports/<int:pk>/approve/', views.committee_problem_report_approve, name='committee_problem_report_approve'),
    path('committee/problem-reports/<int:pk>/reject/', views.committee_problem_report_reject, name='committee_problem_report_reject'),
    path('committee/problem-reports/<int:pk>/delete/', views.committee_problem_report_delete, name='committee_problem_report_delete'),

    # ── Points (user) ───────────────────────────────────────────────────────
    path('points/', views.points, name='points'),
    path('points/submit/', views.point_submit, name='point_submit'),
    path('points/history/', views.point_history, name='point_history'),

    # ── Points (committee) ──────────────────────────────────────────────────
    path('committee/points/', views.committee_points, name='committee_points'),
    path('committee/points/activities/create/', views.committee_point_activity_create, name='committee_point_activity_create'),
    path('committee/points/activities/<int:pk>/edit/', views.committee_point_activity_edit, name='committee_point_activity_edit'),
    path('committee/points/activities/<int:pk>/delete/', views.committee_point_activity_delete, name='committee_point_activity_delete'),
    path('committee/points/submissions/<int:pk>/approve/', views.committee_point_submission_approve, name='committee_point_submission_approve'),
    path('committee/points/submissions/<int:pk>/reject/', views.committee_point_submission_reject, name='committee_point_submission_reject'),
    path('committee/points/submissions/<int:pk>/delete/', views.committee_point_submission_delete, name='committee_point_submission_delete'),
]
