from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

COMMITTEE_CODE = 'COMMITTEE2024'
VALID_EMAIL = 'test@satriwit.ac.th'
PASSWORD = 'Test123!'


def _post_register(client, **overrides):
    data = {
        'email': VALID_EMAIL,
        'password': PASSWORD,
        'verification_code': COMMITTEE_CODE,
    }
    data.update(overrides)
    return client.post(reverse('accounts:register'), data)


class RegisterTest(TestCase):
    """Committee registration promotes an existing roster account."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=VALID_EMAIL, password=PASSWORD, full_name='ทดสอบ', role='student')

    def test_valid_code_promotes_account_to_committee(self):
        resp = _post_register(self.client)
        self.assertRedirects(resp, reverse('portal:dashboard'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'committee')
        self.assertTrue(self.user.is_committee())

    def test_bare_student_id_accepted(self):
        User.objects.create_user(email='12345@satriwit.ac.th', password='12345_5.7',
                                 full_name='ก', role='student')
        _post_register(self.client, email=' 12345 ', password='12345_5.7')
        self.assertEqual(User.objects.get(email='12345@satriwit.ac.th').role, 'committee')

    def test_code_is_case_insensitive(self):
        _post_register(self.client, verification_code=COMMITTEE_CODE.lower())
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'committee')

    def test_wrong_code_rejected(self):
        for code in ('WRONG', 'SW127'):
            resp = _post_register(Client(), verification_code=code)
            self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'student')

    def test_wrong_password_does_not_promote(self):
        resp = _post_register(self.client, password='wrong')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'student')

    def test_unknown_account_rejected(self):
        resp = _post_register(self.client, email='99999@satriwit.ac.th')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email='99999@satriwit.ac.th').exists())

    def test_non_school_email_rejected(self):
        resp = _post_register(self.client, email='test@gmail.com')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'student')


class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email=VALID_EMAIL,
            password=PASSWORD,
            full_name='ทดสอบ',
            role='student',
        )

    def test_login_with_correct_credentials(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': VALID_EMAIL,
            'password': PASSWORD,
        })
        self.assertRedirects(resp, reverse('portal:dashboard'))

    def test_login_with_wrong_password(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': VALID_EMAIL,
            'password': 'wrongpass',
        })
        self.assertEqual(resp.status_code, 200)

    def test_login_with_unknown_email(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'nobody@satriwit.ac.th',
            'password': PASSWORD,
        })
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username=VALID_EMAIL, password=PASSWORD)
        resp = self.client.get(reverse('accounts:login'))
        self.assertRedirects(resp, reverse('portal:dashboard'))

    def test_safe_next_redirect_followed(self):
        resp = self.client.post(
            reverse('accounts:login') + '?next=/dashboard/',
            {'username': VALID_EMAIL, 'password': PASSWORD},
        )
        self.assertRedirects(resp, '/dashboard/', fetch_redirect_response=False)

    def test_unsafe_next_redirect_ignored(self):
        resp = self.client.post(
            reverse('accounts:login') + '?next=https://evil.com/steal',
            {'username': VALID_EMAIL, 'password': PASSWORD},
        )
        self.assertRedirects(resp, reverse('portal:dashboard'))


class LogoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        User.objects.create_user(
            email=VALID_EMAIL, password=PASSWORD, full_name='ทดสอบ', role='student'
        )
        self.client.login(username=VALID_EMAIL, password=PASSWORD)

    def test_post_logout_redirects_to_login(self):
        resp = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(resp, reverse('accounts:login'))

    def test_get_logout_redirects_to_dashboard(self):
        resp = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(resp, reverse('portal:dashboard'))


class ImportStudentsAndLoginTest(TestCase):
    """Uses a tiny synthetic workbook with fake IDs - never real roster data."""

    def _workbook(self, rows):
        import tempfile
        from pathlib import Path

        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = 'ม.5'
        ws.append(['โรงเรียนทดสอบ'])
        ws.append(['รายชื่อนักเรียนระดับมัธยมศึกษาปีที่ 5.10 ภาคเรียนที่ 1'])
        ws.append(['เลขที่', 'เลขประจำตัว', 'ชื่อ-นามสกุล'])
        ws.append(['รายชื่อนักเรียนระดับมัธยมศึกษาปีที่ 5.7 ภาคเรียนที่ 1'])
        for r in rows:
            ws.append(r)
        d = tempfile.mkdtemp()
        path = Path(d) / 'roster.xlsx'
        wb.save(path)
        return str(path)

    def _import(self, rows, *flags):
        from django.core.management import call_command

        call_command('import_students', self._workbook(rows), *flags, stdout=__import__('io').StringIO())

    def test_login_with_email_and_bare_id(self):
        self._import([[1, 11111, 'นาย', 'สมชาย', 'ทดสอบ']])
        user = User.objects.get(email='11111@satriwit.ac.th')
        self.assertEqual((user.student_id, user.classroom, user.grade_level), ('11111', '5.7', 'ม.5'))
        self.assertEqual(user.full_name, 'นายสมชาย ทดสอบ')
        url = reverse('accounts:login')
        for username in ('11111@satriwit.ac.th', ' 11111 ', '11111@SATRIWIT.AC.TH'):
            c = Client()
            resp = c.post(url, {'username': username, 'password': '11111_5.7'})
            self.assertRedirects(resp, reverse('portal:dashboard'), msg_prefix=username)
        bad = Client().post(url, {'username': '11111', 'password': '11111_5.8'})
        self.assertEqual(bad.status_code, 200)

    def test_string_ids_and_idempotent_rerun(self):
        rows = [[1, '22222', 'นาง', 'ก', 'ข'], [2, 33333, 'นาย', 'ค', 'ง']]
        self._import(rows)
        self._import(rows)
        self.assertEqual(User.objects.filter(student_id__in=['22222', '33333']).count(), 2)

    def test_room_change_updates_password(self):
        self._import([[1, 44444, 'นาย', 'ก', 'ข']])
        user = User.objects.get(student_id='44444')
        user.classroom = '5.1'
        user.save()
        self._import([[1, 44444, 'นาย', 'ก', 'ข']])
        user.refresh_from_db()
        self.assertEqual(user.classroom, '5.7')
        self.assertTrue(user.check_password('44444_5.7'))

    def test_committee_account_is_not_touched(self):
        User.objects.create_user(email='55555@satriwit.ac.th', password='Secret123!',
                                 full_name='C', role='committee')
        self._import([[1, 55555, 'นาย', 'ก', 'ข']])
        user = User.objects.get(email='55555@satriwit.ac.th')
        self.assertTrue(user.check_password('Secret123!'))
        self.assertEqual(user.role, 'committee')

    def test_left_school_rows_skipped_by_default(self):
        row = [1, 66666, 'นาย', 'ก', 'ข', None, 'ออก 8 ก.ค. 69']
        self._import([row])
        self.assertFalse(User.objects.filter(student_id='66666').exists())
        self._import([row], '--include-left')
        self.assertTrue(User.objects.filter(student_id='66666').exists())

    def test_dry_run_writes_nothing(self):
        self._import([[1, 77777, 'นาย', 'ก', 'ข']], '--dry-run')
        self.assertFalse(User.objects.filter(student_id='77777').exists())
