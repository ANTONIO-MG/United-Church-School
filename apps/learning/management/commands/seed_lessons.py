"""Seed the demo lessons: Term 1, Week 1 — three days for every grade and subject.

    python manage.py seed_lessons                     # every offering on the UCS spine
    python manage.py seed_lessons --grade 10          # one grade (repeatable)
    python manage.py seed_lessons --subject MATH      # one subject code (repeatable)
    python manage.py seed_lessons --clear             # remove what it made, then rebuild

The content lives in :mod:`core.seed_lessons` (CAPS Term 1 material for 2026);
the rows are built by :mod:`core.seed_lessons.build`. Per offering: a ``T1W1``
topic on the subject's schedule (Term 1 → Week 1), three published lessons
(Day 1–3) each with objectives, notes, a worked example, a YouTube video, a PDF
worksheet, an auto-marked quiz and homework.

Needs the academic spine first (``seed_school_structure``). Idempotent: an
offering that already has its Day lessons is left alone, so teachers' edits
survive a re-run; ``--clear`` removes only what this command created.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core import seed_lessons


class Command(BaseCommand):
    help = 'Seed Term 1 Week 1 demo lessons (Day 1–3, quiz, homework, PDF, video) for every subject.'

    def add_arguments(self, parser):
        parser.add_argument('--grade', type=int, action='append', dest='grades',
                            help='Only this grade (1–12). Repeat for several.')
        parser.add_argument('--subject', action='append', dest='subjects',
                            help='Only this subject code, e.g. MATH or ENG-HL. Repeat for several.')
        parser.add_argument('--clear', action='store_true',
                            help='Delete the lessons/quizzes/homework this command created first.')
        parser.add_argument('--author', default='',
                            help='Username or e-mail recorded as the author (default: first superuser).')

    def handle(self, *args, **opts):
        from core.seed_lessons import build

        problems = seed_lessons.validate()
        if problems:
            for problem in problems[:20]:
                self.stderr.write(f'  {problem}')
            raise CommandError(f'The lesson data has {len(problems)} problem(s).')

        for grade in opts.get('grades') or []:
            if not 1 <= grade <= 12:
                raise CommandError(f'--grade {grade}: grades run from 1 to 12.')
        if not build.offerings_qs().exists():
            raise CommandError('No UCS subject offerings found — run seed_school_structure first.')

        User = get_user_model()
        author = None
        if opts.get('author'):
            author = (User.objects.filter(username=opts['author']).first()
                      or User.objects.filter(email__iexact=opts['author']).first())
            if author is None:
                raise CommandError(f'No user {opts["author"]!r}.')
        else:
            author = User.objects.filter(is_superuser=True).order_by('pk').first()

        verbose = opts.get('verbosity', 1) > 1
        self.stdout.write('Seeding Term 1, Week 1 lessons (Day 1–3) …')
        stats = build.seed(grades=opts.get('grades'), subjects=opts.get('subjects'),
                           clear_first=opts.get('clear'), author=author,
                           log=self.stdout.write if verbose else None)
        if stats.missing:
            self.stdout.write(self.style.WARNING(
                f'  No lesson data for {len(stats.missing)} offering(s): '
                + ', '.join(f'Gr{g} {c}' for g, c in stats.missing)))
        self.stdout.write(self.style.SUCCESS(f'  {stats}'))
