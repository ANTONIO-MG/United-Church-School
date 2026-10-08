"""PDF → structured-JSON generation with Claude (Anthropic).

The "AI route" for authoring: an educator uploads a source PDF (a mock exam, a
set of notes, a past paper with solutions) and Claude returns a **strict JSON
draft** that maps onto our lesson / quiz / assessment models. The draft is saved
in ``draft`` status and reviewed by a human in the normal editor/builder before
being published — the AI never publishes anything itself.

Reuses the enablement gate + model id from :mod:`apps.ai_assistant.admin_ai`
(``ADMIN_AI_ENABLED`` / ``ANTHROPIC_API_KEY`` / ``ADMIN_AI_MODEL``). Claude reads
the PDF natively via a base64 ``document`` content block (no separate text
extraction library needed) and is constrained to our schema with
``output_config.format`` so the response is always valid JSON in the shape we ask
for. Docs: https://platform.claude.com/docs/en/build-with-claude/pdf-support
"""

import base64
import json
import logging

from django.conf import settings

from . import admin_ai

logger = logging.getLogger('apps')

# PDFs Claude reads directly: 32 MB request / 100 pages on a 200k-context model.
MAX_PDF_BYTES = 28 * 1024 * 1024


class GenerationError(Exception):
    """Raised when AI generation is unavailable or the model call failed."""


def is_enabled():
    return admin_ai.is_enabled()


def _extract_json(text):
    """Return the outermost JSON object in ``text`` (handles code fences / prose
    the unconstrained fallback path may add around it)."""
    text = (text or '').strip()
    if text.startswith('```'):
        text = text.split('```', 2)[1] if text.count('```') >= 2 else text
        if text.startswith('json'):
            text = text[4:]
    start, end = text.find('{'), text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1].strip()
    return text.strip()


def _pdf_block(pdf_bytes):
    return {'type': 'document',
            'source': {'type': 'base64', 'media_type': 'application/pdf',
                       'data': base64.standard_b64encode(pdf_bytes).decode('utf-8')}}


def generate_from_prompt(prompt, *, system, schema, instruction,
                         constrain=False, max_tokens=32000):
    """Author from a **written brief** instead of a source document.

    Same contract as :func:`generate_from_pdf` — Claude returns one JSON object
    matching ``schema``, which the caller turns into a draft for a human to
    review. This is the "describe the lesson you want" route in the editor.
    """
    if not is_enabled():
        raise GenerationError(
            'AI authoring is not enabled. Set ADMIN_AI_ENABLED=true and ANTHROPIC_API_KEY.')
    prompt = (prompt or '').strip()
    if not prompt:
        raise GenerationError('Describe what the lesson should cover.')
    content = [{'type': 'text', 'text': 'BRIEF FROM THE EDUCATOR:\n\n' + prompt[:100000]},
               {'type': 'text', 'text': instruction}]
    return _generate(content, system=system, schema=schema, constrain=constrain,
                     max_tokens=max_tokens, label='prompt')


def generate_from_pdf(pdf_bytes, filename, *, system, schema, instruction,
                      extra_docs=None, extra_text=None, extra_prompt='',
                      constrain=True, max_tokens=32000):
    """Send ``pdf_bytes`` (plus any ``extra_docs`` — a list of ``(bytes, label)``
    PDFs, e.g. a memo/solution paper) to Claude and return the parsed JSON object
    matching ``schema``. Raises :class:`GenerationError` on any failure.

    ``constrain`` uses output_config.format (a compiled grammar) for guaranteed
    schema conformance; pass ``False`` for large schemas whose grammar is too
    slow to compile (the schema is put in the prompt instead)."""
    if not is_enabled():
        raise GenerationError(
            'AI authoring is not enabled. Set ADMIN_AI_ENABLED=true and ANTHROPIC_API_KEY.')
    if not pdf_bytes:
        raise GenerationError('The uploaded file was empty.')
    docs = [(pdf_bytes, filename)] + list(extra_docs or [])
    if sum(len(b) for b, _ in docs) > MAX_PDF_BYTES:
        raise GenerationError('The PDFs are too large together (max ~28 MB). Split them and try again.')

    content = [_pdf_block(b) for b, _ in docs]
    if extra_text:
        content.append({'type': 'text',
                        'text': 'MEMO / SOLUTION (extracted from a workbook/document):\n\n'
                                + extra_text[:200000]})
    if extra_prompt:
        content.append({'type': 'text',
                        'text': 'ADDITIONAL DIRECTION FROM THE EDUCATOR:\n\n' + extra_prompt[:20000]})
    content.append({'type': 'text', 'text': instruction})
    return _generate(content, system=system, schema=schema, constrain=constrain,
                     max_tokens=max_tokens, label=filename)


def _generate(content, *, system, schema, constrain, max_tokens, label):
    """One generation round-trip: build the request, stream it, parse the JSON."""
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    filename = label
    messages = [{'role': 'user', 'content': content}]

    def _call(*, constrained):
        """One streamed request. ``constrained`` uses output_config.format (a
        compiled grammar); the fallback path appends the schema to the system
        prompt instead — for schemas whose grammar is too large to compile."""
        kwargs = dict(model=admin_ai._model(), max_tokens=max_tokens, messages=messages)
        if constrained:
            kwargs['system'] = system
            kwargs['output_config'] = {'effort': 'medium',
                                       'format': {'type': 'json_schema', 'schema': schema}}
        else:
            kwargs['system'] = (system + '\n\nRespond with ONLY a single JSON object that '
                                'conforms to this JSON Schema — no prose, no markdown fences:\n'
                                + json.dumps(schema))
            kwargs['output_config'] = {'effort': 'medium'}
        with client.messages.stream(**kwargs) as stream:
            return stream.get_final_message()

    if not constrain:
        try:
            final = _call(constrained=False)
        except Exception as exc:  # pragma: no cover
            logger.exception('ai_assistant.generate: unconstrained call failed for %s', filename)
            raise GenerationError(f'The AI request failed: {exc}')
        if getattr(final, 'stop_reason', '') == 'refusal':
            raise GenerationError('The AI declined to process this document.')
        text = _extract_json(''.join(b.text for b in final.content if getattr(b, 'type', '') == 'text'))
        if not text.strip():
            raise GenerationError('The AI returned an empty response — try a clearer source PDF.')
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise GenerationError('The AI response could not be parsed. Please try again.')

    try:
        final = _call(constrained=True)
    except Exception as exc:  # pragma: no cover - network / API error
        # A schema whose constraint grammar is too large returns a 400
        # "Grammar compilation timed out" — retry unconstrained with the schema
        # in the prompt rather than failing the whole generation.
        if 'grammar' in str(exc).lower():
            logger.warning('ai_assistant.generate: grammar timeout, retrying unconstrained for %s', filename)
            try:
                final = _call(constrained=False)
            except Exception as exc2:  # pragma: no cover
                logger.exception('ai_assistant.generate: fallback call failed for %s', filename)
                raise GenerationError(f'The AI request failed: {exc2}')
        else:
            logger.exception('ai_assistant.generate: model call failed for %s', filename)
            raise GenerationError(f'The AI request failed: {exc}')

    if getattr(final, 'stop_reason', '') == 'refusal':
        raise GenerationError('The AI declined to process this document.')

    text = ''.join(b.text for b in final.content if getattr(b, 'type', '') == 'text')
    # Unconstrained fallback may wrap JSON in prose/fences — extract the object.
    text = _extract_json(text)
    if not text.strip():
        raise GenerationError('The AI returned an empty response — try a clearer source PDF.')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning('ai_assistant.generate: non-JSON response for %s', filename)
        raise GenerationError('The AI response could not be parsed. Please try again.')
