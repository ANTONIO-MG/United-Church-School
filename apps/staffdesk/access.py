"""Who may open the staff desk.

Every page here is an admin / staff tool. The educator dashboard is the one
exception and uses :data:`teaching_required` instead.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from core.errors import note
from core.roles import role_of_user


def staff_required(view):
    """Admin and staff only; everyone else goes back to their dashboard."""
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if role_of_user(request.user) not in ('admin', 'staff'):
            note('DESK-2001', request, view=view.__name__)
            messages.error(request, "That page is for the admin team.")
            return redirect('myhub:index')
        return view(request, *args, **kwargs)
    return wrapped


def teaching_required(view):
    """Educators, plus admin and staff (who can look at any educator's view)."""
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if role_of_user(request.user) not in ('admin', 'staff', 'educator'):
            note('DESK-2001', request, view=view.__name__)
            messages.error(request, "That page is for educators.")
            return redirect('myhub:index')
        return view(request, *args, **kwargs)
    return wrapped
