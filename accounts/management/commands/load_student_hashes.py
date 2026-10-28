import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()

FIELDS = ('full_name', 'student_id', 'classroom', 'grade_level', 'password')


class Command(BaseCommand):
    help = (
        'Load student accounts from a JSON file made by export_students on another machine. '
        'Passwords arrive already hashed, so this is cheap on CPU-limited hosts.'
    )

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **opts):
        path = Path(opts['path'])
        if not path.is_file():
            raise CommandError(f'File not found: {path}')
        rows = json.loads(path.read_text(encoding='utf-8'))

        created = updated = 0
        protected = []
        for row in rows:
            if not row['password'].startswith('pbkdf2_'):
                raise CommandError('Unexpected password format; expected a pre-hashed value')
            user = User.objects.filter(email=row['email']).first()
            if user is None:
                User.objects.create(email=row['email'], role='student', **{f: row[f] for f in FIELDS})
                created += 1
            elif user.role == 'committee' or user.is_staff or user.is_superuser:
                protected.append(row['email'])
            else:
                for f in FIELDS:
                    setattr(user, f, row[f])
                user.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. created={created} updated={updated} protected={len(protected)}'))
        for e in protected:
            self.stdout.write(f'  not touched: {e}')
