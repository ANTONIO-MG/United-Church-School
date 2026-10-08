"""On-demand academic-intelligence summaries (admin/staff/educator only).

Each function is guarded so a missing table never breaks a dashboard. Heavy
exports use openpyxl when available. Natural-language insight can reuse the
existing local AI (apps.ai_assistant) — kept optional.
"""

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


def student_summary():
    """Active/inactive student counts + recent login activity."""
    try:
        from apps.accounts.models import Person
        now = timezone.now()
        students = Person.objects.filter(user_type='student')
        total = students.count()
        active = User.objects.filter(profile__user_type='student', is_active=True).count()
        logged_today = User.objects.filter(profile__user_type='student',
                                           last_login__date=now.date()).count()
        logged_week = User.objects.filter(profile__user_type='student',
                                          last_login__gte=now - timedelta(days=7)).count()
        return {
            'total': total, 'active': active, 'inactive': max(0, total - active),
            'logged_today': logged_today, 'logged_week': logged_week,
        }
    except Exception:
        logger.exception('student_summary failed')
        return {}


def module_popularity(limit=10):
    """Most-enrolled module offerings."""
    try:
        from apps.learning.models import ProgrammeModule
        return list(ProgrammeModule.objects.annotate(enrolled=Count('enrolments'))
                    .order_by('-enrolled')[:limit]
                    .values('name', 'enrolled'))
    except Exception:
        logger.exception('module_popularity failed')
        return []


def module_performance(limit=20):
    """Average mark / pass rate per module from computed grades."""
    try:
        from apps.reports.models import Grade
        rows = (Grade.objects.values('module__name')
                .annotate(avg_mark=Avg('final_pct'), students=Count('id'),
                          passes=Count('id', filter=Q(passed=True)))
                .order_by('-avg_mark')[:limit])
        out = []
        for r in rows:
            students = r['students'] or 0
            out.append({
                'module': r['module__name'],
                'avg_mark': round(float(r['avg_mark'] or 0), 1),
                'students': students,
                'pass_rate': round((r['passes'] / students * 100) if students else 0, 1),
            })
        return out
    except Exception:
        logger.exception('module_performance failed')
        return []


def study_summary():
    """Aggregate study hours + completed sessions (native lessons + SCORM)."""
    try:
        from apps.learning.models import StudySession
        from django.db.models import Sum
        aggregated = StudySession.objects.aggregate(
            total_seconds=Sum('total_seconds'), session_count=Count('id'))
        completed = StudySession.objects.filter(status='completed').count()
        data = {
            'total_hours': round((aggregated['total_seconds'] or 0) / 3600.0, 1),
            'sessions': aggregated['session_count'] or 0, 'completed': completed,
        }
        # Fold in imported SCORM activity so external content is visible too.
        try:
            from apps.scorm.models import ScormAttempt
            sc = ScormAttempt.objects.aggregate(secs=Sum('total_seconds'), n=Count('id'))
            done = sum(1 for a in ScormAttempt.objects.only('completion_status', 'lesson_status') if a.is_complete)
            data['scorm_attempts'] = sc['n'] or 0
            data['scorm_completed'] = done
            data['total_hours'] = round(data['total_hours'] + (sc['secs'] or 0) / 3600.0, 1)
        except Exception:
            pass
        return data
    except Exception:
        logger.exception('study_summary failed')
        return {}


def institution_dashboard():
    """One-call executive summary for the analytics landing page."""
    data = {
        'students': student_summary(),
        'popular': module_popularity(),
        'modules': module_performance(),
        'study': study_summary(),
    }
    try:
        from apps.reports.models import Certificate
        from apps.learning.models import ProgrammeModule
        data['certificates_issued'] = Certificate.objects.count()
        data['total_modules'] = ProgrammeModule.objects.count()
    except Exception:
        pass
    try:
        from apps.learning.models import Lesson
        data['total_lessons'] = Lesson.objects.count()
    except Exception:
        pass
    return data


def compute_risk(student):
    """Heuristic predictive-risk score (0–100) for a student, with reasons."""
    reasons = []
    score = 0
    try:
        from apps.reports.models import Grade
        from apps.learning.models import StudySession
        from apps.assessments.models import AssessmentAttempt

        failing = Grade.objects.filter(student=student, passed=False).count()
        if failing:
            score += min(40, failing * 20)
            reasons.append(f'{failing} failing module(s)')

        recent_study = StudySession.objects.filter(
            student=student, created_at__gte=timezone.now() - timedelta(days=14)).count()
        if recent_study == 0:
            score += 30
            reasons.append('No study sessions in 14 days')

        recent_fail = AssessmentAttempt.objects.filter(
            student=student, passed=False,
            submitted_at__gte=timezone.now() - timedelta(days=30)).count()
        if recent_fail >= 3:
            score += 30
            reasons.append(f'Failed {recent_fail} assessments recently')
    except Exception:
        logger.exception('compute_risk failed')
    return min(100, score), reasons


def export_rows_xlsx(rows, headers, filename='report.xlsx'):
    """Return (filename, bytes) for an Excel export, or (None, None) if openpyxl is absent."""
    try:
        import io
        from openpyxl import Workbook
    except Exception:
        return None, None
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h, '') if isinstance(row, dict) else row for h in headers])
    buf = io.BytesIO()
    wb.save(buf)
    return filename, buf.getvalue()
