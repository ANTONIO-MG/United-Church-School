"""Back-fill the tasks that deliver already-published lessons and assessments.

From now on, publishing a lesson or an assessment creates the task that tracks it
(``apps.tasks.signals``). Content published *before* that link existed has no
task, so it never reaches a learner's task list or the calendar. This command
walks that back-catalogue once.

Deliberately a command rather than a data migration: creating tasks fans out a
``TaskAssignment`` per targeted learner, which is a visible change to everyone's
task list. That should be someone's decision, made when they are ready — and
``--dry-run`` lets them see the size of it first.

    python manage.py sync_activity_tasks --dry-run
    python manage.py sync_activity_tasks
    python manage.py sync_activity_tasks --lessons-only
"""

from django.core.management.base import BaseCommand

from apps.tasks import activities
from apps.tasks.models import Task


class Command(BaseCommand):
    help = 'Create the delivering task for lessons/assessments published before the two were linked.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Report what would be created without writing anything.')
        parser.add_argument('--lessons-only', action='store_true', help='Skip assessments.')
        parser.add_argument('--assessments-only', action='store_true', help='Skip lessons.')

    def handle(self, *args, **options):
        from apps.assessments.models import Assessment
        from apps.learning.models import Lesson

        dry = options['dry_run']
        created = skipped = 0

        targets = []
        if not options['assessments_only']:
            targets.append(('lesson', Lesson.objects.filter(
                status__in=(Lesson.STATUS_PUBLISHED, Lesson.STATUS_SCHEDULED))))
        if not options['lessons_only']:
            targets.append(('assessment', Assessment.objects.filter(
                status__in=(Assessment.STATUS_OPEN, Assessment.STATUS_SCHEDULED))))

        for label, queryset in targets:
            for activity in queryset.iterator():
                if Task.objects.filter(**{label: activity}).exists():
                    skipped += 1
                    continue
                if dry:
                    self.stdout.write(f'  would create: [{label}] {activity.title}')
                    created += 1
                    continue
                task = activities.sync_task_for(activity)
                if task is None:
                    skipped += 1
                    continue
                created += 1
                self.stdout.write(
                    f'  created: [{task.kind_label}] {task.title} '
                    f'→ {task.assignments.count()} assignee(s)')

        verb = 'Would create' if dry else 'Created'
        self.stdout.write(self.style.SUCCESS(
            f'{verb} {created} task(s); {skipped} already linked or not publishable.'))
