"""``manage.py errorcheck`` — audit the error dictionary against the source.

Three questions, answered from the code itself rather than from memory:

1. Is every entry in the catalog well-formed (valid prefix, cause class, and all
   four remedy fields filled in)?
2. Does every code *referenced in the source* exist in the catalog? A typo'd code
   is worse than no code — it logs an error whose dictionary page says nothing.
3. Which parts of the codebase raise errors but have no tagged code yet? That is
   coverage, and it is reported per module so it can be worked down.

Exits non-zero when anything is wrong, so CI can run it as a gate.
"""

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.diagnostics import catalog

# Any 'XXX-1234' literal in a string, which is how codes are always written.
CODE_RE = re.compile(r"""['"]([A-Z]{2,5}-\d{4})['"]""")
# Places that produce an error a user or developer might have to act on.
ERROR_SITE_RE = re.compile(
    r'\b(except\s+\w|messages\.error\(|logger\.(?:exception|error)\(|'
    r'raise\s+(?:ValidationError|PermissionDenied|Http404)|HttpResponseForbidden\()')
TAG_RE = re.compile(r"\b(?:report|note|fail|capture|errorcode)\(\s*['\"][A-Z]{2,5}-\d{4}")

SKIP_PARTS = {'__pycache__', 'migrations', 'node_modules', '.env', 'staticfiles', 'vendor'}


def source_files():
    base = Path(settings.BASE_DIR)
    for root in ('apps', 'core', 'config'):
        for path in (base / root).rglob('*.py'):
            if SKIP_PARTS & set(path.parts) or path.name == 'tests.py':
                continue
            yield path


class Command(BaseCommand):
    help = 'Audit the error catalog against the codebase.'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true',
                            help='List every untagged module, not just the summary.')

    def handle(self, *args, **options):
        problems = []

        # 1. The catalog itself
        catalog_problems = catalog.validate()
        problems.extend(catalog_problems)

        # 2. Codes used in the source
        used, unknown = set(), {}
        untagged, tagged_modules = {}, set()
        for path in source_files():
            text = path.read_text(encoding='utf-8', errors='ignore')
            rel = str(path.relative_to(settings.BASE_DIR))
            # The catalog *defines* codes rather than referencing them, and this
            # checker quotes example codes in its own docstring and patterns.
            if rel.endswith(('diagnostics/catalog.py', 'commands/errorcheck.py')):
                continue
            for code in CODE_RE.findall(text):
                used.add(code)
                if not catalog.exists(code):
                    unknown.setdefault(code, []).append(rel)
            if TAG_RE.search(text):
                tagged_modules.add(rel)
            elif ERROR_SITE_RE.search(text):
                untagged[rel] = len(ERROR_SITE_RE.findall(text))

        for code, files in sorted(unknown.items()):
            problems.append(f'{code} is used in {", ".join(sorted(set(files)))} '
                            f'but is not in the catalog')

        unused = sorted(set(catalog.ERRORS) - used)

        # --- Report ---
        self.stdout.write(self.style.MIGRATE_HEADING('Error catalog'))
        self.stdout.write(f'  documented codes : {len(catalog.ERRORS)}')
        self.stdout.write(f'  domains          : {len(catalog.PREFIXES)}')
        self.stdout.write(f'  referenced in code: {len(used & set(catalog.ERRORS))}')
        if catalog_problems:
            self.stdout.write(self.style.ERROR(f'  malformed entries : {len(catalog_problems)}'))
        if unknown:
            self.stdout.write(self.style.ERROR(f'  unknown codes used: {len(unknown)}'))

        self.stdout.write(self.style.MIGRATE_HEADING('\nCoverage'))
        self.stdout.write(f'  modules with explicit codes : {len(tagged_modules)}')
        self.stdout.write(f'  modules with untagged errors: {len(untagged)}')
        self.stdout.write(self.style.WARNING(
            '  (untagged failures are still logged — the logging handler auto-classifies\n'
            '   them — but they arrive as a generic code with a generic remedy.)'))
        if untagged and options['verbose']:
            for rel, count in sorted(untagged.items(), key=lambda kv: -kv[1])[:40]:
                self.stdout.write(f'    {count:>3} error site(s)  {rel}')

        if unused:
            self.stdout.write(self.style.MIGRATE_HEADING(
                f'\nDocumented but never referenced ({len(unused)})'))
            self.stdout.write(self.style.WARNING(
                '  Reachable only via auto-classification, or documenting a condition\n'
                '  that has no explicit tag yet. Not an error in itself.'))
            self.stdout.write('  ' + ', '.join(unused))

        if problems:
            self.stdout.write(self.style.ERROR(f'\n{len(problems)} problem(s):'))
            for problem in problems:
                self.stdout.write(self.style.ERROR(f'  • {problem}'))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS('\nThe error catalog is consistent with the code.'))
