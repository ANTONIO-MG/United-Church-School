"""DRF serializers for the MyHub domain.

All that survives the clean sweep is the calendar: the professor / student /
course / library / fees / CMS / blog models this module used to serialise went
with the old MyHub theme. See :mod:`apps.myhub.api`.
"""

from rest_framework import serializers

from . import models


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'
