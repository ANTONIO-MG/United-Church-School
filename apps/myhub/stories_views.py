"""The school's stories — the public pages behind the landing page's "Read more".

The stories themselves are data (:mod:`core.stories`, imported from the Info Hub
on www.ucs.org.za); these views only lay them out in the landing page's style.
Both pages are public: ``/social/stories/`` is exempt from the login gate in
:mod:`apps.accounts.middleware`.
"""

from django.http import Http404
from django.shortcuts import render

from core import stories


def _blocks(paragraphs):
    """Paragraph strings → ``[{'type': 'p'|'h'|'ul', ...}]`` for the template.

    ``"## "`` starts a sub-heading and ``"• "`` a list item (see core.stories);
    consecutive list items are gathered into one list.
    """
    blocks = []
    for text in paragraphs:
        if text.startswith('## '):
            blocks.append({'type': 'h', 'text': text[3:].strip()})
        elif text.startswith('• '):
            if not blocks or blocks[-1]['type'] != 'ul':
                blocks.append({'type': 'ul', 'items': []})
            blocks[-1]['items'].append(text[2:].strip())
        else:
            blocks.append({'type': 'p', 'text': text})
    return blocks


def story_index(request):
    """Every story, newest first."""
    return render(request, 'pages/stories/index.html', {
        'page_title': 'UCS Stories',
        'stories': stories.all_stories(),
    })


def story_detail(request, slug):
    """One story, in full, with the next few to read."""
    story = stories.get(slug)
    if story is None:
        raise Http404('No such story')
    others = [s for s in stories.all_stories() if s['slug'] != slug][:3]
    return render(request, 'pages/stories/detail.html', {
        'page_title': story['title'],
        'story': story,
        'blocks': _blocks(story['body']),
        'others': others,
    })
