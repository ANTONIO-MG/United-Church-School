import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_subject_program'),
        ('learning', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('kind', models.CharField(choices=[('quiz', 'Quiz'), ('test', 'Test'), ('exam_section', 'Exam section'), ('assignment', 'Assignment')], db_index=True, default='quiz', max_length=12)),
                ('description', models.TextField(blank=True)),
                ('total_marks', models.DecimalField(decimal_places=2, default=100, max_digits=7)),
                ('pass_mark_pct', models.PositiveIntegerField(default=50)),
                ('time_limit_minutes', models.PositiveIntegerField(default=0, help_text='0 = no limit.')),
                ('attempts_allowed', models.PositiveIntegerField(default=1, help_text='0 = unlimited.')),
                ('timer_behaviour', models.CharField(choices=[('continue', 'Continue if browser closes'), ('pause', 'Pause'), ('autosubmit', 'Auto submit')], default='autosubmit', max_length=12)),
                ('shuffle_questions', models.BooleanField(default=False)),
                ('available_from', models.DateTimeField(blank=True, null=True)),
                ('available_to', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')], db_index=True, default='draft', max_length=10)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessments_created', to=settings.AUTH_USER_MODEL)),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessments', to='learning.lesson')),
                ('module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessments', to='learning.module')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessments', to='accounts.subject')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('instructions', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='assessments.assessment')),
            ],
            options={'ordering': ['assessment', 'order']},
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('mcq', 'Multiple choice'), ('multi', 'Multiple select'), ('tf', 'True / False'), ('matching', 'Matching'), ('ordering', 'Ordering'), ('fill', 'Fill in the blank'), ('short', 'Short answer'), ('long', 'Long answer'), ('essay', 'Essay'), ('image_select', 'Image selection'), ('diagram', 'Diagram labeling'), ('audio_resp', 'Audio response'), ('video_resp', 'Video response'), ('file_upload', 'File upload'), ('project', 'Project submission'), ('coding', 'Coding exercise')], default='mcq', max_length=14)),
                ('text', models.TextField()),
                ('marks', models.DecimalField(decimal_places=2, default=1, max_digits=6)),
                ('order', models.PositiveIntegerField(default=0)),
                ('media', models.FileField(blank=True, null=True, upload_to='questions/')),
                ('config', models.JSONField(blank=True, default=dict)),
                ('marking', models.JSONField(blank=True, default=dict)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='assessments.section')),
            ],
            options={'ordering': ['section', 'order']},
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=400)),
                ('is_correct', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='assessments.question')),
            ],
            options={'ordering': ['question', 'order']},
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('available_from', models.DateTimeField(blank=True, null=True)),
                ('available_to', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('scheduled', 'Scheduled'), ('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')], db_index=True, default='draft', max_length=10)),
                ('lock_after_submit', models.BooleanField(default=True)),
                ('invigilator_mode', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exams_created', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to='accounts.subject')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ExamSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('weight', models.DecimalField(decimal_places=2, default=1, max_digits=5)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_sections', to='assessments.assessment')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_sections', to='assessments.exam')),
            ],
            options={'ordering': ['exam', 'order'], 'unique_together': {('exam', 'assessment')}},
        ),
        migrations.CreateModel(
            name='AssessmentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('public_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('in_progress', 'In progress'), ('submitted', 'Submitted'), ('marked', 'Marked')], db_index=True, default='in_progress', max_length=12)),
                ('attempt_no', models.PositiveIntegerField(default=1)),
                ('started_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('time_spent_seconds', models.PositiveIntegerField(default=0)),
                ('score', models.DecimalField(decimal_places=2, default=0, max_digits=7)),
                ('passed', models.BooleanField(default=False)),
                ('draft', models.JSONField(blank=True, default=dict)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='assessments.assessment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('assessment', 'student', 'attempt_no')}},
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.JSONField(blank=True, default=dict)),
                ('file', models.FileField(blank=True, null=True, upload_to='answers/')),
                ('awarded_marks', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('is_correct', models.BooleanField(default=False)),
                ('flagged_for_review', models.BooleanField(default=False)),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='assessments.assessmentattempt')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='assessments.question')),
                ('selected_choices', models.ManyToManyField(blank=True, related_name='answers', to='assessments.choice')),
            ],
            options={'unique_together': {('attempt', 'question')}},
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('assigned', 'Assigned'), ('started', 'Started'), ('draft', 'Draft'), ('submitted', 'Submitted'), ('marked', 'Marked'), ('returned', 'Returned'), ('resubmission', 'Resubmission requested'), ('completed', 'Completed')], db_index=True, default='assigned', max_length=14)),
                ('text', models.TextField(blank=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='assignments/')),
                ('grade', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='assessments.assessment')),
                ('marked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments_marked', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('assessment', 'student')}},
        ),
    ]
