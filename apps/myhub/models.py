"""Domain models backing the MyHub dashboard pages.

Each user-facing section of the dashboard (Professors, Students,
Courses, Library, Staff, Holidays, Fees and the CMS) is represented here so the
corresponding HTML pages can list / create / edit / delete real records.
"""

import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

PUBLISH_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
# ---------------------------------------------------------------------------
# Events / Calendar
# ---------------------------------------------------------------------------
class Event(TimeStampedModel):
    CATEGORY_EVENT = 'event'
    CATEGORY_REMINDER = 'reminder'
    CATEGORY_CHOICES = [(CATEGORY_EVENT, 'Event'), (CATEGORY_REMINDER, 'Reminder')]

    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=20, blank=True, default='#3a87ad')
    description = models.TextField(blank=True)

    # When ``owner`` is set the event is personal (a reminder / private entry)
    # and only that user sees it on the calendar; otherwise it is institution-wide.
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name='calendar_events',
    )
    category = models.CharField(max_length=12, choices=CATEGORY_CHOICES, default=CATEGORY_EVENT)

    class Meta:
        ordering = ['start']

    def __str__(self):
        return self.title
