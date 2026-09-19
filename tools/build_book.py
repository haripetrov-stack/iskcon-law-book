"""Builds book.html from the generated original. Usage: python tools/build_book.py [path-to-original]"""
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
  .law-container.lvl1 { padding: 20px 12px 8px; }
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

PREFILL_SCRIPT = """<script>
document.addEventListener('DOMContentLoaded', function() {
  var q = new URLSearchParams(location.search).get('q');
  if (!q) return;
  var input = document.getElementById('searchInput');
  input.value = q;
  input.dispatchEvent(new Event('input'));
});
</script>"""


def insert_after_line(data, marker, block, eol):
    if data.count(marker) != 1:
        raise SystemExit(f'expected exactly one {marker!r} in the original, found {data.count(marker)}')
    line_end = data.index(eol, data.index(marker)) + len(eol)
    return data[:line_end] + block.replace('\n', eol) + eol + data[line_end:]


def build(data):
    eol = '\r\n' if '\r\n' in data[:2000] else '\n'
    data = insert_after_line(data, '<title>', FAVICON, eol)
    data = insert_after_line(data, '</style>', SITE_STYLE, eol)
    data = insert_after_line(data, '<body>', TOPBAR, eol)
    data = insert_after_line(data, '</script>', PREFILL_SCRIPT, eol)
    return data


def main():
    data = ORIGINAL.read_text(encoding='utf-8', newline='')
    out = build(data)
    (ROOT / 'book.html').write_text(out, encoding='utf-8', newline='')
    print(f'book.html: {len(out.encode("utf-8")):,} bytes from {ORIGINAL}')


if __name__ == '__main__':
    main()
