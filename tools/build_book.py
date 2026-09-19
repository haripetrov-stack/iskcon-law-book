"""Builds book.html from the generated original. Usage: python tools/build_book.py [path-to-original]"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    'D:/AI_OS/Repos/personal/elm-ai-presentation/law-book-output/00 iskcon-law-v6-2018-2026.html')

FAVICON = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 16 16\'%3E'
           '%3Crect width=\'16\' height=\'16\' rx=\'3\' fill=\'%231E2761\'/%3E'
           '%3Cpath d=\'M4 4.5h8M4 8h8M4 11.5h5\' stroke=\'%23D99A2B\' stroke-width=\'1.8\' stroke-linecap=\'round\'/%3E%3C/svg%3E">')

SITE_STYLE = """<style>
.topbar { font-family: var(--sans); font-size: 0.88em; background: #1E2761; color: #CADCFC; padding: 8px 24px; display: flex; gap: 18px; align-items: center; flex-wrap: wrap; }
.topbar .topbar-title { color: #fff; margin-right: auto; }
.topbar a { color: #D99A2B; text-decoration: none; }
.topbar a:hover { text-decoration: underline; }
.chapter-shell { padding: 26px 24px 10px; border-top: 3px double var(--line); }
.chapter-shell .law-head { font-size: 1.7em; border-bottom: 2px solid var(--accent); padding-bottom: 6px; }
.chapter-hint { font-family: var(--sans); font-size: 0.85em; color: var(--muted); margin: 8px 0 0; }
@media (max-width: 640px) {
  header.cover { padding: 24px 16px 16px; }
  header.cover h1 { font-size: 1.6em; }
  .wrap { padding: 0 16px 60px; }
  .topbar { padding: 6px 16px; gap: 14px; }
  .searchbar { padding: 8px 16px; }
  .searchbar input[type=search] { flex-basis: 100%; min-width: 0; }
  nav.toc { padding: 16px; }
  .toc-controls { float: none; margin: 0 0 10px; }
  nav.toc ol { padding-left: 14px; }
  .law-container.lvl1, .chapter-shell { padding: 20px 12px 8px; }
  .law-container.lvl2, .law-container.lvl3, .law-container.lvl4, .law-container.lvl5, .law-container.lvl6 { padding-left: 10px; }
  .chapter-general-block { margin-left: 0; }
  .article { padding: 12px 12px 14px; }
  .node-body p, .article .body p { text-align: left; }
  body { overflow-wrap: anywhere; }
  table.crosswalk-table, table.book-table { display: block; overflow-x: auto; overflow-wrap: normal; }
  table.crosswalk-table > tbody, table.book-table > tbody { display: table; border-collapse: collapse; }
  table.crosswalk-table > tbody { width: 100%; min-width: 36rem; }
  footer.build { padding: 24px 16px 40px; }
}
</style>"""

TOPBAR = """<div class="topbar no-print">
  <span class="topbar-title">ISKCON Law, working draft</span>
  <a href="index.html">About this draft</a>
  <a href="iskcon-law-draft-2018-2026.pdf">PDF</a>
</div>"""

RUNTIME_SCRIPT = """<script>
(function() {
  var UNIT = '.article, .own-content';
  var VISIBLE = '.article:not(.hidden), .own-content:not(.hidden)';
  var input = document.getElementById('searchInput');
  var chapters = [], idToChapter = {}, terms = [], articles = 0;
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) { if (e.isIntersecting) expand(idToChapter[e.target.id], false); });
  }, { rootMargin: '600px 0px' });

  Array.prototype.forEach.call(document.querySelectorAll('template.chapter-src'), function(t) {
    var ch = {
      id: t.dataset.chapter, template: t, shell: document.getElementById(t.dataset.chapter), live: null, bySearch: false,
      noHide: t.content.querySelector('.law-container.lvl1').classList.contains('no-hide'),
      units: Array.prototype.map.call(t.content.querySelectorAll(UNIT), function(el) {
        return { text: el.textContent.toLowerCase(), match: true };
      })
    };
    Array.prototype.forEach.call(t.content.querySelectorAll('[id]'), function(el) { idToChapter[el.id] = ch; });
    articles += t.content.querySelectorAll('.article').length;
    chapters.push(ch);
    observer.observe(ch.shell);
  });

  function elements(ch, selector) {
    var out = [];
    ch.live.forEach(function(n) {
      if (n.nodeType !== 1) return;
      if (n.matches(selector)) out.push(n);
      out.push.apply(out, n.querySelectorAll(selector));
    });
    return out;
  }
  function filter(ch) {
    var units = elements(ch, UNIT);
    ch.units.forEach(function(u, i) { units[i].classList.toggle('hidden', !u.match); });
    elements(ch, '.law-container').forEach(function(c) {
      c.classList.toggle('hidden', terms.length > 0 && !c.classList.contains('no-hide') && !c.querySelector(VISIBLE));
    });
    elements(ch, '.chapter-general-block').forEach(function(c) {
      c.classList.toggle('hidden', terms.length > 0 && !c.querySelector('.article:not(.hidden)'));
    });
  }
  function expand(ch, bySearch) {
    if (!ch.live) {
      var clone = document.importNode(ch.template.content, true);
      ch.live = Array.prototype.slice.call(clone.childNodes);
      ch.shell.replaceWith(clone);
      ch.bySearch = true;
      if (terms.length) filter(ch);
    }
    ch.bySearch = ch.bySearch && bySearch;
  }
  function collapse(ch) {
    if (!ch.live) return;
    ch.live[0].parentNode.insertBefore(ch.shell, ch.live[0]);
    ch.live.forEach(function(n) { n.parentNode.removeChild(n); });
    ch.live = null;
    ch.bySearch = false;
    observer.observe(ch.shell);
  }
  function search() {
    terms = input.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    var shown = 0, total = 0;
    chapters.forEach(function(ch) {
      var hits = 0, wasLive = !!ch.live;
      ch.units.forEach(function(u) {
        u.match = terms.every(function(t) { return u.text.indexOf(t) !== -1; });
        if (u.match) hits++;
      });
      shown += hits;
      total += ch.units.length;
      if (!terms.length) { ch.shell.classList.remove('hidden'); if (ch.bySearch) collapse(ch); }
      else if (hits) expand(ch, true);
      else if (!ch.noHide) { collapse(ch); ch.shell.classList.add('hidden'); }
      if (wasLive && ch.live) filter(ch);
    });
    document.getElementById('resultCount').textContent = terms.length ? (shown + ' of ' + total + ' sections/entries match') : (articles + ' entries total');
  }
  function follow() {
    var id = decodeURIComponent(location.hash.slice(1));
    var ch = idToChapter[id];
    if (!ch) return;
    expand(ch, false);
    document.getElementById(id).scrollIntoView();
  }

  input.addEventListener('input', search);
  document.getElementById('clearBtn').addEventListener('click', function() { input.value = ''; search(); });
  document.getElementById('expandAllBtn').addEventListener('click', function() {
    document.querySelectorAll('#tocNav details').forEach(function(d) { d.open = true; });
  });
  document.getElementById('collapseAllBtn').addEventListener('click', function() {
    document.querySelectorAll('#tocNav details').forEach(function(d) { d.open = false; });
  });
  window.addEventListener('hashchange', follow);
  window.addEventListener('beforeprint', function() { chapters.forEach(function(ch) { expand(ch, false); }); });
  var q = new URLSearchParams(location.search).get('q');
  if (q) input.value = q;
  search();
  follow();
})();
</script>"""

HINT = 'Opens when you scroll here, search, or follow a link.'
CONTENT_OPEN = re.compile(r'<div\b[^>]*\bid="content"[^>]*>')
CHAPTER_OPEN = re.compile(r'<(?:div|section) class="law-container lvl1[^"]*" id="([^"]+)">')
TOC_COUNT = re.compile(r'<a href="#([^"]+)">[^<]*</a> <span class="count">\(([^)]*)\)</span>')
H2 = re.compile(r'<h2 class="law-head">.*?</h2>', re.S)


def insert_after_line(data, marker, block, eol):
    if data.count(marker) != 1:
        raise SystemExit(f'expected exactly one {marker!r} in the original, found {data.count(marker)}')
    line_end = data.index(eol, data.index(marker)) + len(eol)
    return data[:line_end] + block.replace('\n', eol) + eol + data[line_end:]


def content_bounds(data):
    start = CONTENT_OPEN.search(data)
    depth = 0
    for tag in re.finditer(r'<div\b|</div\s*>', data[start.start():]):
        depth += 1 if tag.group().startswith('<div') else -1
        if depth == 0:
            return start.end(), start.start() + tag.start()
    raise SystemExit('#content is not closed')


def chapter_chunks(inner):
    """Splits the inner HTML of #content at every top-level chapter start. Concatenated, the chunks equal the input."""
    depth, starts = 0, []
    for tag in re.finditer(r'<(/?)(div|section)\b[^>]*>', inner):
        if tag.group(1):
            depth -= 1
        else:
            if depth == 0 and CHAPTER_OPEN.match(tag.group()):
                starts.append(tag.start())
            depth += 1
    return [inner[a:b] for a, b in zip([0] + starts[1:], starts[1:] + [len(inner)])]


def hint(counts):
    if not counts:
        return HINT
    counts = re.sub(r'\bentries\b', 'sections', re.sub(r'\bentry\b', 'section', counts))
    return f'{counts}. {HINT}'


def lazy_chapters(data, eol):
    begin, end = content_bounds(data)
    inner = data[begin:end]
    if '<script' in inner or '</template>' in inner:
        raise SystemExit('#content contains a script or template tag; the transform would break it')
    toc_counts = dict(TOC_COUNT.findall(data[data.index('<nav class="toc'):data.index('</nav>')]))
    parts = []
    for chunk in chapter_chunks(inner):
        cid = CHAPTER_OPEN.search(chunk).group(1)
        parts.append(f'<div class="chapter-shell" id="{cid}" data-chapter="{cid}">{H2.search(chunk).group()}'
                     f'<p class="chapter-hint">{hint(toc_counts.get(cid))}</p></div>{eol}'
                     f'<template class="chapter-src" data-chapter="{cid}">{chunk}</template>{eol}')
    return data[:begin] + eol + ''.join(parts) + data[end:], len(parts)


def build(data):
    eol = '\r\n' if '\r\n' in data[:2000] else '\n'
    data = insert_after_line(data, '<title>', FAVICON, eol)
    data = insert_after_line(data, '</style>', SITE_STYLE, eol)
    data = insert_after_line(data, '<body>', TOPBAR, eol)
    if data.count('<script') != 1:
        raise SystemExit(f'expected exactly one script in the original, found {data.count("<script")}')
    data = data[:data.index('<script>')] + RUNTIME_SCRIPT.replace('\n', eol) + data[data.index('</script>') + len('</script>'):]
    return lazy_chapters(data, eol)


def main():
    out, count = build(ORIGINAL.read_text(encoding='utf-8', newline=''))
    (ROOT / 'book.html').write_text(out, encoding='utf-8', newline='')
    print(f'book.html: {len(out.encode("utf-8")):,} bytes, {count} lazy chapters, from {ORIGINAL}')


if __name__ == '__main__':
    main()
