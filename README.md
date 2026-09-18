# ISKCON Law: a searchable working draft

A small static site for the ELM 2026 talk. It holds the 2018 ISKCON Law Book Update, extended with every published GBC resolution from 2019 to 2026, as one searchable HTML page and one PDF.

Published at `https://haripetrov-stack.github.io/iskcon-law-book/`.

## Status

An unapproved working draft, generated automatically on 27 August 2026. Not reviewed or authorised by the GBC. An authorised committee must review which provisions remain in force and resolve conflicts.

## Files

- `index.html`: the landing page (what the draft is, status, buttons, three sample searches).
- `book.html`: the draft itself, 1.2 MB, with the search built in. `book.html?q=succession` opens it with the search prefilled. The book text, the table of contents and the search script are the generated originals. The site adds one `<style>` block for phones, a top bar, a favicon and one short `<script>` for the `?q=` prefill.
- `iskcon-law-draft-2018-2026.pdf`: the same draft as a PDF, 10 MB, 422 pages.
- `.nojekyll`: tells GitHub Pages to serve the files as they are.
- `tools/check.py`: the static check described below.

## Rerunning the check

```
python tools/check.py
```

It prints one line per check and exits with code 1 on any failure. It checks that the `<div id="content">` element of `book.html` is byte-identical to the generated original, that no `src`, `<link href>`, `@import` or `url()` points to an `http(s)://` address, that every local link on both pages resolves to a file, that `.nojekyll` exists, and it prints the file sizes.

The original is read from `D:\AI_OS\Repos\personal\elm-ai-presentation\law-book-output\00 iskcon-law-v6-2018-2026.html` by default. Pass another path as the first argument to compare against a different copy.

Browser checks (no horizontal scrolling at 390 px, search counts, console errors) are run by hand with Playwright against a local `python -m http.server`.
