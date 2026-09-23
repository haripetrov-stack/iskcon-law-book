"""Static checks for the site. Usage: python tools/check.py [path-to-original-book.html]"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    'D:/AI_OS/Repos/personal/elm-ai-presentation/law-book-output/archive/00 iskcon-law-v6-2018-2026.html')
PAGES = ['index.html', 'book.html']
SIZED = ['index.html', 'book.html', 'iskcon-law-draft-2018-2026.pdf', 'tools/check.py']

EXTERNAL_REF = re.compile(
    r'\bsrc\s*=\s*["\']?https?://'
    r'|<link\b[^>]*\bhref\s*=\s*["\']?https?://'
    r'|@import\s+(?:url\()?["\']?https?://'
    r'|url\(\s*["\']?https?://', re.I)
LOCAL_REF = re.compile(r'\b(?:href|src)="([^"]*)"')
SKIP_REF = re.compile(r'^(?:https?:|mailto:|data:|javascript:|#)', re.I)
TEMPLATE = re.compile(rb'<template class="chapter-src" data-chapter="[^"]*">(.*?)</template>', re.S)
LIVE_ELEMENT_BUDGET = 2000


def content_inner(data):
    start = re.search(rb'<div\b[^>]*\bid="content"[^>]*>', data)
    if not start:
        return None
    depth = 0
    for tag in re.finditer(rb'<div\b|</div\s*>', data[start.start():]):
        depth += 1 if tag.group().startswith(b'<div') else -1
        if depth == 0:
            return data[start.end():start.start() + tag.start()]
    return None


def check_content_identical():
    if not ORIGINAL.is_file():
        return False, f'original not found: {ORIGINAL}'
    ours = content_inner((ROOT / 'book.html').read_bytes())
    theirs = content_inner(ORIGINAL.read_bytes())
    if ours is None or theirs is None:
        return False, '#content element not found in one of the files'
    templates = TEMPLATE.findall(ours)
    joined = b''.join(templates)
    return bool(templates) and joined == theirs, (
        f'{len(templates)} chapter templates, {len(joined):,} bytes in book.html, {len(theirs):,} bytes in the original')


def check_live_elements():
    """Elements the browser builds at load: every tag in book.html outside the chapter templates."""
    data = (ROOT / 'book.html').read_bytes()
    live = len(re.findall(rb'<[a-zA-Z]', TEMPLATE.sub(b'', data)))
    return live <= LIVE_ELEMENT_BUDGET, f'{live:,} elements outside templates, budget {LIVE_ELEMENT_BUDGET:,}'


def check_no_external_requests(page):
    hits = [m.group() for m in EXTERNAL_REF.finditer((ROOT / page).read_text(encoding='utf-8'))]
    return not hits, f'{page}: {len(hits)} external src/link/import/url() references' + (f' {hits[:3]}' if hits else '')


def check_local_refs(page):
    refs = sorted({r for r in LOCAL_REF.findall((ROOT / page).read_text(encoding='utf-8')) if not SKIP_REF.match(r)})
    missing = [r for r in refs if not (ROOT / re.split(r'[?#]', r)[0]).is_file()]
    return not missing, f'{page}: {len(refs)} local references, {len(missing)} missing' + (f' {missing}' if missing else '')


def check_nojekyll():
    return (ROOT / '.nojekyll').is_file(), '.nojekyll present' if (ROOT / '.nojekyll').is_file() else '.nojekyll missing'


def check_sizes():
    parts = [f'{name} {(ROOT / name).stat().st_size:,} B' for name in SIZED if (ROOT / name).is_file()]
    return len(parts) == len(SIZED), '; '.join(parts)


def main():
    checks = [
        ('chapter templates identical to the original #content', check_content_identical),
        ('live elements at load within budget', check_live_elements),
        *[(f'no external requests in {p}', lambda p=p: check_no_external_requests(p)) for p in PAGES],
        *[(f'local references exist in {p}', lambda p=p: check_local_refs(p)) for p in PAGES],
        ('.nojekyll', check_nojekyll),
        ('file sizes', check_sizes),
    ]
    failed = 0
    for name, fn in checks:
        ok, detail = fn()
        failed += not ok
        print(f'{"PASS" if ok else "FAIL"} {name}: {detail}')
    print(f'{len(checks) - failed} of {len(checks)} checks passed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
