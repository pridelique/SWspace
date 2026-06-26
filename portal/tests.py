from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


def _make_uploaded_file(name='test.jpg', content_type='image/jpeg'):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    buf = BytesIO()
    fmt = 'PNG' if 'png' in name else 'JPEG'
    Image.new('RGB', (1, 1), color=(200, 50, 50)).save(buf, format=fmt)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=content_type)


class ImageUploadTest(TestCase):
    """
    Verifies committee create/edit views correctly save uploaded images
    to local media storage (ImageField), and that access control is enforced.
    """

    def setUp(self):
        self.committee = User.objects.create_user(
            email='committee@satriwit.ac.th',
            password='Test123!',
            full_name='คณะกรรมการ',
            role='committee',
        )
        self.student = User.objects.create_user(
            email='student@satriwit.ac.th',
            password='Test123!',
            full_name='นักเรียน',
            role='student',
        )
        self.c_client = Client()
        self.c_client.login(username='committee@satriwit.ac.th', password='Test123!')
        self.s_client = Client()
        self.s_client.login(username='student@satriwit.ac.th', password='Test123!')

    # ── News: create ──────────────────────────────────────────────────────────

    def test_news_create_with_image_saves(self):
        resp = self.c_client.post(
            reverse('portal:committee_news_create'),
            {
                'title': 'ข่าวมีรูป',
                'description': 'รายละเอียด',
                'category': 'internal',
                'is_published': True,
                'image': _make_uploaded_file(),
            },
        )
        self.assertRedirects(resp, reverse('portal:committee_news_list'))
        from portal.models import News
        item = News.objects.get(title='ข่าวมีรูป')
        self.assertTrue(bool(item.image))

    def test_news_create_without_image_saves(self):
        resp = self.c_client.post(
            reverse('portal:committee_news_create'),
            {
                'title': 'ข่าวไม่มีรูป',
                'description': 'รายละเอียด',
                'category': 'external',
                'is_published': True,
            },
        )
        self.assertRedirects(resp, reverse('portal:committee_news_list'))
        from portal.models import News
        item = News.objects.get(title='ข่าวไม่มีรูป')
        self.assertFalse(bool(item.image))

    # ── News: edit ────────────────────────────────────────────────────────────

    def test_news_edit_with_image_replaces(self):
        from portal.models import News
        item = News.objects.create(
            title='ข่าวเดิม', description='desc', category='internal',
            created_by=self.committee,
        )
        resp = self.c_client.post(
            reverse('portal:committee_news_edit', args=[item.pk]),
            {
                'title': 'ข่าวเดิม',
                'description': 'desc',
                'category': 'internal',
                'is_published': True,
                'image': _make_uploaded_file(),
            },
        )
        self.assertRedirects(resp, reverse('portal:committee_news_list'))
        item.refresh_from_db()
        self.assertTrue(bool(item.image))

    # ── Competition: create ───────────────────────────────────────────────────

    def test_competition_create_with_image_saves(self):
        resp = self.c_client.post(
            reverse('portal:committee_competition_create'),
            {
                'title': 'การแข่งขันทดสอบ',
                'description': 'รายละเอียด',
                'is_published': True,
                'image': _make_uploaded_file('comp.png', 'image/png'),
            },
        )
        self.assertRedirects(resp, reverse('portal:committee_competition_list'))
        from portal.models import Competition
        item = Competition.objects.get(title='การแข่งขันทดสอบ')
        self.assertTrue(bool(item.image))

    def test_competition_create_without_image_saves(self):
        resp = self.c_client.post(
            reverse('portal:committee_competition_create'),
            {
                'title': 'การแข่งขันไม่มีรูป',
                'description': 'รายละเอียด',
                'is_published': True,
            },
        )
        self.assertRedirects(resp, reverse('portal:committee_competition_list'))
        from portal.models import Competition
        self.assertTrue(Competition.objects.filter(title='การแข่งขันไม่มีรูป').exists())

    # ── Permission: student blocked ───────────────────────────────────────────

    def test_student_cannot_create_news(self):
        resp = self.s_client.post(
            reverse('portal:committee_news_create'),
            {'title': 'hack', 'description': 'hack', 'category': 'internal'},
        )
        self.assertIn(resp.status_code, [301, 302])
        from portal.models import News
        self.assertFalse(News.objects.filter(title='hack').exists())

    def test_student_cannot_create_competition(self):
        resp = self.s_client.post(
            reverse('portal:committee_competition_create'),
            {'title': 'hack', 'description': 'hack'},
        )
        self.assertIn(resp.status_code, [301, 302])
        from portal.models import Competition
        self.assertFalse(Competition.objects.filter(title='hack').exists())

    # ── GET renders (regression) ──────────────────────────────────────────────

    def test_news_create_form_renders(self):
        self.assertEqual(
            self.c_client.get(reverse('portal:committee_news_create')).status_code, 200
        )

    def test_competition_create_form_renders(self):
        self.assertEqual(
            self.c_client.get(reverse('portal:committee_competition_create')).status_code, 200
        )


class PointsTest(TestCase):
    """Tests for point collection feature."""

    def setUp(self):
        self.committee = User.objects.create_user(
            email='committee@satriwit.ac.th',
            password='Test123!',
            full_name='คณะกรรมการ',
            role='committee',
        )
        self.student = User.objects.create_user(
            email='student@satriwit.ac.th',
            password='Test123!',
            full_name='นักเรียน',
            role='student',
        )
        self.c_client = Client()
        self.c_client.login(username='committee@satriwit.ac.th', password='Test123!')
        self.s_client = Client()
        self.s_client.login(username='student@satriwit.ac.th', password='Test123!')

        from portal.models import PointActivity
        self.activity = PointActivity.objects.create(
            title='ทดสอบ',
            points=10,
            is_active=True,
            created_by=self.committee,
        )

    def _submit(self):
        from portal.models import PointSubmission
        return PointSubmission.objects.create(
            activity=self.activity,
            submitted_by=self.student,
            proof_image=_make_uploaded_file(),
            status=PointSubmission.STATUS_PENDING,
        )

    # ── Student views ──────────────────────────────────────────────────────────

    def test_points_page_renders(self):
        self.assertEqual(self.s_client.get(reverse('portal:points')).status_code, 200)

    def test_point_history_renders(self):
        self.assertEqual(self.s_client.get(reverse('portal:point_history')).status_code, 200)

    def test_student_cannot_access_committee_points(self):
        resp = self.s_client.get(reverse('portal:committee_points'))
        self.assertIn(resp.status_code, [301, 302])

    # ── Submission submit ──────────────────────────────────────────────────────

    def test_submit_proof_creates_pending(self):
        from portal.models import PointSubmission
        resp = self.s_client.post(
            reverse('portal:point_submit'),
            {
                'activity': self.activity.pk,
                'proof_image': _make_uploaded_file(),
            },
        )
        self.assertRedirects(resp, reverse('portal:points'))
        sub = PointSubmission.objects.get(submitted_by=self.student, activity=self.activity)
        self.assertEqual(sub.status, PointSubmission.STATUS_PENDING)

    # ── Approve idempotent ─────────────────────────────────────────────────────

    def test_approve_adds_points(self):
        from portal.models import PointSubmission, UserPointProfile
        sub = self._submit()
        self.c_client.post(reverse('portal:committee_point_submission_approve', args=[sub.pk]))
        profile = UserPointProfile.objects.get(user=self.student)
        self.assertEqual(profile.total_points, self.activity.points)
        sub.refresh_from_db()
        self.assertEqual(sub.status, PointSubmission.STATUS_APPROVED)

    def test_approve_twice_does_not_double_add(self):
        from portal.models import PointSubmission, UserPointProfile
        sub = self._submit()
        self.c_client.post(reverse('portal:committee_point_submission_approve', args=[sub.pk]))
        self.c_client.post(reverse('portal:committee_point_submission_approve', args=[sub.pk]))
        profile = UserPointProfile.objects.get(user=self.student)
        self.assertEqual(profile.total_points, self.activity.points)

    # ── Reject guard ───────────────────────────────────────────────────────────

    def test_reject_approved_submission_blocked(self):
        from portal.models import PointSubmission
        sub = self._submit()
        sub.status = PointSubmission.STATUS_APPROVED
        sub.save()
        resp = self.c_client.post(
            reverse('portal:committee_point_submission_reject', args=[sub.pk]),
            {'admin_note': 'เหตุผล'},
        )
        self.assertRedirects(resp, reverse('portal:committee_points'))
        sub.refresh_from_db()
        self.assertEqual(sub.status, PointSubmission.STATUS_APPROVED)

    def test_reject_pending_changes_status(self):
        from portal.models import PointSubmission
        sub = self._submit()
        self.c_client.post(
            reverse('portal:committee_point_submission_reject', args=[sub.pk]),
            {'admin_note': 'ไม่ครบ'},
        )
        sub.refresh_from_db()
        self.assertEqual(sub.status, PointSubmission.STATUS_REJECTED)
        self.assertEqual(sub.admin_note, 'ไม่ครบ')
