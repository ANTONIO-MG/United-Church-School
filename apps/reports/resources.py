"""django-import-export resources for marks and certificates.

Grades are **export-only**: they are computed from assessments, tasks and study
time by :mod:`apps.reports.services`, so letting a spreadsheet write them back
would silently overwrite the calculation. What an administrator or educator
actually needs is to get the marks *out* — into a spreadsheet, a mark schedule or
an external system — which is what these resources do.
"""

from import_export import fields, resources

from . import models


class GradeResource(resources.ModelResource):
    """A report-card row per student per module, ready for a spreadsheet."""

    student = fields.Field(column_name='student', attribute='student__email', readonly=True)
    student_name = fields.Field(column_name='student_name', readonly=True)
    module = fields.Field(column_name='module', attribute='module__name', readonly=True)
    course = fields.Field(column_name='course', attribute='module__course__title', readonly=True)
    assignments = fields.Field(column_name='assignments_pct', readonly=True)
    quizzes = fields.Field(column_name='quizzes_pct', readonly=True)
    tests = fields.Field(column_name='tests_pct', readonly=True)
    exams = fields.Field(column_name='exams_pct', readonly=True)
    tasks = fields.Field(column_name='tasks_pct', readonly=True)

    class Meta:
        model = models.Grade
        fields = ('student', 'student_name', 'course', 'module', 'final_pct', 'letter',
                  'passed', 'class_position', 'cohort_size', 'cohort_average',
                  'assignments', 'quizzes', 'tests', 'exams', 'tasks',
                  'attendance_pct', 'study_hours', 'computed_at')
        export_order = fields

    def dehydrate_student_name(self, grade):
        from core.utils import display_name
        return display_name(grade.student) or ''

    # The per-component breakdown lives in a JSON blob; flatten it to one column
    # each so the spreadsheet is sortable and chartable.
    def _component(self, grade, key):
        return (grade.components or {}).get(key, '')

    def dehydrate_assignments(self, grade):
        return self._component(grade, 'assignments')

    def dehydrate_quizzes(self, grade):
        return self._component(grade, 'quizzes')

    def dehydrate_tests(self, grade):
        return self._component(grade, 'tests')

    def dehydrate_exams(self, grade):
        return self._component(grade, 'exams')

    def dehydrate_tasks(self, grade):
        return self._component(grade, 'tasks')


class CertificateResource(resources.ModelResource):
    """Issued certificates — number, holder, mark and verification link."""

    student = fields.Field(column_name='student', attribute='student__email', readonly=True)
    module = fields.Field(column_name='module', attribute='module__name', readonly=True)
    course = fields.Field(column_name='course', attribute='course__title', readonly=True)

    class Meta:
        model = models.Certificate
        fields = ('number', 'student', 'kind', 'title', 'course', 'module',
                  'final_mark', 'issued_at', 'verification_uuid')
        export_order = fields
