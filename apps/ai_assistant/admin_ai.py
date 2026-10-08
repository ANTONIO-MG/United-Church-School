"""The admin AI layer — the advanced, Claude-powered institutional analyst.

This is the *second* AI layer in the dual-layer design (see the project notes):
the first layer is the local CrewAI assistant available to everyone; this layer
is a paid, token-billed Claude model reserved for admins/staff. It answers
deep-dive institutional questions — trend reports, risk assessments, cross-class
summaries — grounded in the analytics summaries the platform already computes.

Everything here is optional and graceful: if the ``anthropic`` SDK isn't
installed or ``ANTHROPIC_API_KEY`` isn't set, :func:`is_enabled` is False and the
view shows a friendly "not configured" message instead of erroring.

Config (settings / ``.env``)::

    ADMIN_AI_ENABLED = True
    ANTHROPIC_API_KEY = "sk-ant-..."
    ADMIN_AI_MODEL = "claude-opus-4-8"   # the advanced, paid model ("Claude Next")
"""

import logging

from django.conf import settings

logger = logging.getLogger(__name__)

try:  # The Anthropic SDK is an optional dependency.
    import anthropic
    ANTHROPIC_AVAILABLE = True
except Exception:  # pragma: no cover - SDK not installed
    anthropic = None
    ANTHROPIC_AVAILABLE = False


SYSTEM_PROMPT = (
    "You are the school analytics assistant for the learning platform of United Church "
    "School, an independent Grade 1-12 school in Yeoville, Johannesburg, following the "
    "South African CAPS curriculum. You serve administrators and staff only. Your job is deep, "
    "school-level analysis: trends across grades, classes and subjects, risk assessment "
    "for at-risk learners, cross-class comparisons, and concise, actionable summaries "
    "for leadership. Ground every claim in the analytics snapshot provided in the "
    "context. When the data is insufficient, say so plainly rather than inventing "
    "numbers. Be direct and lead with the headline finding."
)


def is_enabled():
    """True when the admin AI is switched on, configured, and importable."""
    return bool(
        getattr(settings, 'ADMIN_AI_ENABLED', False)
        and getattr(settings, 'ANTHROPIC_API_KEY', '')
        and ANTHROPIC_AVAILABLE
    )


def _model():
    return getattr(settings, 'ADMIN_AI_MODEL', '') or 'claude-opus-4-8'


def _institutional_context():
    """A compact snapshot of institutional analytics for grounding the model.

    Reuses :mod:`apps.analytics.services` so the admin AI sees the same numbers
    the analytics dashboard shows. Never raises — returns '' on any error.
    """
    try:
        from apps.analytics import services as a
        parts = []
        for name in ('student_summary', 'module_popularity', 'module_performance',
                     'study_summary'):
            fn = getattr(a, name, None)
            if callable(fn):
                try:
                    parts.append(f'{name}: {fn()}')
                except Exception:
                    continue
        try:
            from apps.analytics.models import RiskFlag
            parts.append(f'open_risk_flags: {RiskFlag.objects.filter(resolved=False).count()}')
        except Exception:
            pass
        return '\n'.join(str(p) for p in parts)[:12000]
    except Exception:  # pragma: no cover
        logger.exception('admin_ai: could not build institutional context')
        return ''


def ask(history, question):
    """Send the conversation to Claude and return ``(answer, usage_dict)``.

    ``history`` is a list of ``{'role': 'user'|'assistant', 'content': str}``
    dicts (the prior turns); ``question`` is the new user message. Returns
    ``(text, {'input_tokens', 'output_tokens', 'model'})``. Never raises — on a
    failure it returns a friendly message and zeroed usage.
    """
    if not is_enabled():
        return (
            "The admin AI isn't configured yet. An administrator needs to install the "
            "`anthropic` package and set `ANTHROPIC_API_KEY` (and `ADMIN_AI_ENABLED=True`) "
            "in the environment.",
            {'input_tokens': 0, 'output_tokens': 0, 'model': ''},
        )

    context = _institutional_context()
    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nCurrent institutional analytics snapshot:\n{context}"

    messages = [{'role': m['role'], 'content': m['content']} for m in history
                if m.get('content')]
    messages.append({'role': 'user', 'content': question})

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        # Adaptive thinking + streaming, per the Claude API guidance: stream so a
        # long institutional analysis can't hit the request timeout, then collect
        # the final message for the answer text and token usage.
        with client.messages.stream(
            model=_model(),
            max_tokens=16000,
            system=system,
            thinking={'type': 'adaptive'},
            output_config={'effort': 'high'},
            messages=messages,
        ) as stream:
            final = stream.get_final_message()
        answer = ''.join(b.text for b in final.content if getattr(b, 'type', '') == 'text')
        usage = {
            'input_tokens': getattr(final.usage, 'input_tokens', 0) or 0,
            'output_tokens': getattr(final.usage, 'output_tokens', 0) or 0,
            'model': getattr(final, 'model', _model()),
        }
        return answer or '(no answer)', usage
    except Exception as exc:  # pragma: no cover - never break the request
        logger.exception('admin_ai ask failed')
        return (f"The admin AI hit an error: {exc}", {'input_tokens': 0, 'output_tokens': 0, 'model': _model()})
