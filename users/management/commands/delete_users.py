'''
Delete SQL users and their Mongo listings / related docs.

Azure SSH / Kudu (from wwwroot):

  python manage.py delete_users --email ch1@gmail.com
  python manage.py delete_users --email ch1@gmail.com --yes
  python manage.py delete_users --user-id 12 --yes
  python manage.py delete_users --all --yes

Staff/superusers are skipped unless --include-staff is passed.
Without --yes this is a dry run (counts only, nothing deleted).
'''

from django.core.management.base import BaseCommand, CommandError

from users.management.purge_ops import delete_users, resolve_users
from users.models import User


class Command(BaseCommand):
    help = 'Delete users from SQL and their Mongo data. Dry-run unless --yes is passed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete every non-staff user (add --include-staff to include admins).',
        )
        parser.add_argument(
            '--email',
            action='append',
            default=[],
            help='User email or username. Repeatable.',
        )
        parser.add_argument(
            '--user-id',
            action='append',
            dest='user_ids',
            default=[],
            help='SQL user id. Repeatable.',
        )
        parser.add_argument(
            '--include-staff',
            action='store_true',
            help='Also delete is_staff / is_superuser accounts.',
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Actually delete. Omit this flag to preview counts.',
        )

    def handle(self, *args, **options):
        delete_all = options['all']
        emails = options['email']
        raw_ids = options['user_ids']
        include_staff = options['include_staff']
        dry_run = not options['yes']

        if not delete_all and not emails and not raw_ids:
            raise CommandError(
                'Pass --all, or --email / --user-id to choose which users to delete.'
            )
        if delete_all and (emails or raw_ids):
            raise CommandError('Use either --all or --email/--user-id, not both.')

        if delete_all:
            qs = User.objects.all()
            if not include_staff:
                qs = qs.filter(is_staff=False, is_superuser=False)
            users = list(qs)
        else:
            users = resolve_users(
                emails=emails,
                user_ids=raw_ids,
                include_staff=include_staff,
            )

        if not users:
            raise CommandError('No matching users found (staff are skipped by default).')

        self.stdout.write(
            'Users: ' + ', '.join(f'{u.id}:{u.email or u.username}' for u in users)
        )
        summary = delete_users(users=users, dry_run=dry_run)
        label = 'Dry run (no deletes)' if dry_run else 'Deleted'
        self.stdout.write(self.style.WARNING(label) if dry_run else self.style.SUCCESS(label))
        for name, count in summary.items():
            self.stdout.write(f'  {name}: {count}')
        if dry_run:
            self.stdout.write('Re-run the same command with --yes to delete.')
