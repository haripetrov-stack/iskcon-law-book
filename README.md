# ISKCON Law: a searchable working draft

A small static site for the ELM 2026 talk. It holds the 2018 ISKCON Law Book Update, extended with every published GBC resolution from 2019 to 2026, as one searchable HTML page and one PDF.

Published at `https://haripetrov-stack.github.io/iskcon-law-book/`.

## Status

An unapproved working draft, generated automatically on 27 August 2026. Not reviewed or authorised by the GBC. An authorised committee must review which provisions remain in force and resolve conflicts.

## Files

- `index.html`: the landing page (what the draft is, status, buttons, three sample searches).
- `book.html`: the draft itself, 1.2 MB, with the search built in. `book.html?q=succession` opens it with the search prefilled. The book text and the table of contents are the generated originals. The site adds one `<style>` block for phones and the top bar, a favicon, and one `<script>` that replaces the original search script (see below).
- `tools/build_book.py`: builds `book.html` from the generated original in one command. Rerun it after every change to the original or to the site additions.
- `--standalone OUT.html` writes the same lazy page without the site top bar, as one file that can be sent by e-mail and opened from disk.
- `iskcon-law-draft-2018-2026.pdf`: the same draft as a PDF, 10 MB, 422 pages.
- `.nojekyll`: tells GitHub Pages to serve the files as they are.
- `tools/check.py`: the static check described below.

## Lazy chapters

The original page put all 31 chapters into the DOM at once: 16,470 elements, and opening a table of contents entry froze the browser. `book.html` now keeps each chapter inside an inert `<template class="chapter-src">` and shows a short shell in its place (the chapter heading and a hint line). The page script expands a chapter when its shell scrolls near the viewport, when a search matches text in it, when a link or the URL hash points into it, and before printing. Clearing the search collapses the chapters the search opened. The search index is built from the templates, so the counts are the same as before. The chapter text is untouched: the templates, concatenated, are byte-identical to the original `#content`. Build it with:

```
python tools/build_book.py
python tools/build_book.py --standalone D:/path/to/iskcon-law-draft.html
```

The script reads the original from the same default path as the check and takes another path as its first argument.

## Rerunning the check

```
python tools/check.py
```

It prints one line per check and exits with code 1 on any failure. It checks that the chapter templates in `book.html`, concatenated, are byte-identical to the inner HTML of the generated original's `<div id="content">`, that at most 2,000 elements sit outside the templates (what the browser builds at load), that no `src`, `<link href>`, `@import` or `url()` points to an `http(s)://` address, that every local link on both pages resolves to a file, that `.nojekyll` exists, and it prints the file sizes.

The original is read from `D:\AI_OS\Repos\personal\elm-ai-presentation\law-book-output\00 iskcon-law-v6-2018-2026.html` by default. Pass another path as the first argument to compare against a different copy.

Browser checks (no horizontal scrolling at 390 px, search counts, console errors) are run by hand with Playwright against a local `python -m http.server`.
