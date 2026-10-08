"""Keep the media directory tidy: delete files the database no longer points at.

Django never deletes the file behind a ``FileField``/``ImageField`` on its own —
not when the row is deleted, and not when the field is pointed at a new upload.
Over time that leaves orphans on disk (old profile pictures, replaced logos,
attachments of deleted messages).

:func:`register` wires two signals for a model:

* **pre_save**  — if a monitored field now holds a *different* file from the row
  already in the database, delete the old file.  (This is the "replace a picture
  and the old one is removed" behaviour.)
* **post_delete** — when the row goes, delete the file(s) it owned.

Storage ``.delete()`` is best-effort and never raises into the request: a missing
or already-gone file must not break a save.

Register once per model from the app's ``AppConfig.ready()`` — see
``apps.accounts.apps`` / ``apps.communication.apps``.
"""

import logging

from django.db.models.signals import post_delete, pre_save

logger = logging.getLogger('apps')


def _delete_file(fieldfile):
    """Remove the file behind a FieldFile from storage, if it is really there."""
    if not fieldfile:
        return
    name = getattr(fieldfile, 'name', '')
    if not name:
        return
    storage = fieldfile.storage
    try:
        if storage.exists(name):
            storage.delete(name)
    except Exception:  # pragma: no cover - never let cleanup break the request
        logger.warning('file_cleanup: could not delete %s', name, exc_info=True)


def register(model, fields):
    """Auto-clean the given file ``fields`` of ``model`` on replace and on delete."""
    field_names = tuple(fields)
    uid = f'filecleanup:{model._meta.label}'

    def on_pre_save(sender, instance, **kwargs):
        if instance.pk is None:
            return                      # brand-new row: nothing to replace yet
        try:
            old = sender.objects.only(*field_names).get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        for name in field_names:
            old_file = getattr(old, name, None)
            new_file = getattr(instance, name, None)
            # Changed to a different file (or cleared) → the old one is now an orphan.
            if old_file and old_file.name != getattr(new_file, 'name', None):
                _delete_file(old_file)

    def on_post_delete(sender, instance, **kwargs):
        for name in field_names:
            _delete_file(getattr(instance, name, None))

    pre_save.connect(on_pre_save, sender=model, weak=False, dispatch_uid=uid + ':save')
    post_delete.connect(on_post_delete, sender=model, weak=False, dispatch_uid=uid + ':del')
