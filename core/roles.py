"""Shared helpers for role-aware data scoping + permissions.

Roles (see ``apps.accounts.models.USER_TYPE_CHOICES``): student, parent, educator,
staff, admin. Anonymous visitors have no role ('' — the site is private, they are
redirected to login by LoginRequiredMiddleware).

Permission model:
  • admin / staff  — full CRUD on everything (``can_manage``).
  • educator       — teach-only: view their courses/modules/students + teaching
                     actions (mark/grade, attendance, lessons, announcements). NO
                     create/edit/delete of courses/modules/people (``can_teach``).
  • student        — view their own data only.
  • parent         — view their child's data + make payments (``can_pay``).

:func:`role_flags` exposes these to views and (via the ``user_roles`` context
processor) to every template so the sidebar shows the right sections.
"""


def role_of_user(user):
    """Return a user's role string ('' for anonymous / missing users).

    The user-object counterpart of :func:`role_of` — handy where you have a
    ``User`` but no request (e.g. deciding whether two people are both students).
    """
    if user is None or not getattr(user, 'is_authenticated', False):
        return ''
    person = getattr(user, 'profile', None)
    role = getattr(person, 'user_type', None) or 'student'
    if (user.is_staff or user.is_superuser) and role not in ('admin', 'staff'):
        # Treat Django staff/superusers as admins for visibility purposes.
        role = 'admin'
    return role


def role_of(request):
    """Return the current user's role string ('' for anonymous visitors)."""
    return role_of_user(getattr(request, 'user', None))


def role_flags(request):
    """Return a dict of boolean role + permission flags and the role string."""
    role = role_of(request)
    user = getattr(request, 'user', None)
    is_admin_staff = role in ('admin', 'staff') or bool(
        user and (user.is_staff or user.is_superuser))
    is_educator = role == 'educator'
    is_parent = role == 'parent'
    return {
        'user_role': role,
        'is_admin_staff': is_admin_staff,
        'is_admin': role == 'admin' or bool(user and user.is_superuser),
        'is_staff_member': role == 'staff' or bool(user and user.is_staff),
        'is_educator': is_educator,
        'is_parent': is_parent,
        'is_student': role == 'student',
        # --- Permission flags ---
        'can_manage': is_admin_staff,                 # full CRUD (admin/staff only)
        'can_teach': is_admin_staff or is_educator,   # teaching actions (mark/attend/lessons)
        'can_pay': is_admin_staff or is_parent or role == 'student',  # make payments
    }


def user_roles(request):
    """Context processor: expose role + permission flags to every template.

    For a parent it also names the child their pages are about, so the nav can
    say "Sam's tasks" rather than "Tasks". The lookup is skipped entirely for
    everyone else, so this costs a query only on parent requests.
    """
    flags = role_flags(request)
    if flags['is_parent']:
        flags.update(_parent_context(request))
    return flags


def _parent_context(request):
    """``child`` / ``child_name`` / ``children`` for a parent's templates."""
    try:
        from core.scoping import children_of, viewing_child
        child = viewing_child(request)
        return {
            'child': child,
            'child_name': (child.get_full_name() or child.get_username()) if child else '',
            'children': children_of(getattr(request, 'user', None)),
        }
    except Exception:  # pragma: no cover - the nav must never 500 a page
        return {'child': None, 'child_name': '', 'children': None}
