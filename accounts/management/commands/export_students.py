import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Export roster-based student accounts (with hashed passwords) to JSON for load_student_hashes.'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **opts):
        qs = User.objects.filter(
            student_id__isnull=False, is_staff=False, is_superuser=False,
        ).order_by('student_id')
        rows = list(qs.values('email', 'full_name', 'student_id', 'classroom', 'grade_level', 'password'))
        Path(opts['path']).write_text(json.dumps(rows, ensure_ascii=False), encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'Exported {len(rows)} students to {opts["path"]}'))
