'''
Delete marketplace listings from Mongo (category collections + listsync).

Azure SSH / Kudu (from wwwroot):

  python manage.py delete_listings --all
  python manage.py delete_listings --all --yes
  python manage.py delete_listings --email ch1@gmail.com --yes
  python manage.py delete_listings --user-id 12 --yes

Without --yes this is a dry run (counts only, nothing deleted).
'''

from django.core.management.base import BaseCommand, CommandError

from users.management.purge_ops import delete_listings, resolve_users


class Command(BaseCommand):
    help = 'Delete listings from Mongo. Dry-run unless --yes is passed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete every marketplace listing.',
        )
        parser.add_argument(
            '--email',
            action='append',
            default=[],
            help='Only listings owned by this user email/username. Repeatable.',
        )
        parser.add_argument(
            '--user-id',
            action='append',
            dest='user_ids',
            default=[],
            help='Only listings owned by this SQL user id. Repeatable.',
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
        dry_run = not options['yes']

        if not delete_all and not emails and not raw_ids:
            raise CommandError(
                'Pass --all, or --email / --user-id to choose whose listings to delete.'
            )
        if delete_all and (emails or raw_ids):
            raise CommandError('Use either --all or --email/--user-id, not both.')

        user_ids = None
        if not delete_all:
            users = resolve_users(emails=emails, user_ids=raw_ids, include_staff=True)
            if not users:
                raise CommandError('No matching users found.')
            user_ids = [u.id for u in users]
            self.stdout.write(
                'Users: ' + ', '.join(f'{u.id}:{u.email or u.username}' for u in users)
            )

        summary = delete_listings(user_ids=user_ids, dry_run=dry_run)
        label = 'Dry run (no deletes)' if dry_run else 'Deleted'
        self.stdout.write(self.style.WARNING(label) if dry_run else self.style.SUCCESS(label))
        for name, count in summary.items():
            self.stdout.write(f'  {name}: {count}')
        if dry_run:
            self.stdout.write('Re-run the same command with --yes to delete.')
