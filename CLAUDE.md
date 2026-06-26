# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

# Superuser email must end with @satriwit.ac.th
python manage.py createsuperuser

python manage.py runserver          # http://127.0.0.1:8000/
python manage.py test               # all tests
python manage.py test accounts      # single app
python manage.py test portal
```

If port 8000 is stuck on Windows:
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Stop-Process -Id <PID> -Force
```

## Architecture

Django 4.2 project with two apps (`accounts`, `portal`) and a top-level `templates/` directory.

### User model (`accounts/models.py`)

Custom `AbstractUser` subclass using **email as the login field** (no `username`). Two roles:
- `student` — default
- `committee` — granted at registration if the user enters the verification code from `settings.COMMITTEE_VERIFICATION_CODE`

Email must end with `settings.STUDENT_EMAIL_DOMAIN` (`@satriwit.ac.th`). Both constants live in `config/settings.py` and are hardcoded (see TODO in settings for production guidance).

`User.is_committee()` is the canonical role check used throughout the codebase.

### Access control (`portal/views.py`)

Two decorators guard portal views:
- `@login_required` — all portal views
- `@committee_required` — custom decorator defined in `portal/views.py`, wraps `@login_required` and checks `is_committee()`

Do not use `@staff_member_required` or `@permission_required` — the project uses the `committee` role, not Django staff/permissions.

### Portal models (`portal/models.py`)

Five models, all with `is_published`/`is_approved` flags and `created_by`/`submitted_by` FK to `AUTH_USER_MODEL`:

| Model | Flag | Who creates |
|-------|------|-------------|
| `News` | `is_published` | committee |
| `VolunteerLink` | `is_published` | committee |
| `Competition` | `is_published` | committee |
| `StudyNote` | `is_approved` (defaults True) | any student |
| `ProblemReport` | `status` (pending/approved/rejected) | any student |

Committee views for each model follow the pattern `committee_{model}_list/create/edit/delete` in `portal/views.py` and `portal/urls.py`.

### URL structure

Root URL (`/`) redirects to `/dashboard/` via `root_redirect` in `config/urls.py`.

- `/accounts/` — auth (login, register, logout) via `accounts.urls`
- `/` (everything else) — portal via `portal.urls` (app_name `portal`)

### Templates

All templates extend `templates/base.html`. Layout:
```
templates/
  base.html
  accounts/    login.html, register.html
  portal/      dashboard.html, news.html, volunteer.html, competitions.html,
               study_notes.html, problem_reports.html, study_note_form.html,
               problem_report_form.html, committee.html,
               committee_{model}_list/form/confirm_delete.html (×4 models)
               committee_problem_report_reject_form.html
               committee_study_note_confirm_delete.html
```
