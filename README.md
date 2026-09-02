# datedavid.org

A single-file, radically transparent dating page. The premise: a dating radius of
two astronomical seconds (2 s of the Sun's motion relative to the cosmic microwave
background, ~740 km), an airline remix that converts the radius into a wall-clock
travel budget, and a full disclosure of the life plan behind it — family, wedding,
money, geography, dealbreakers — with every factual claim paired to an audit prompt
the reader can paste into any AI assistant.

## How it works

- **One static file.** Everything is `index.html`: hand-written CSS, vanilla JS,
  no framework, no build step, no dependencies beyond Google Fonts.
  `404.html` is the only other page; it redirects `/family`-style paths to
  `/#family` and otherwise links home. A `<noscript>` block shows every
  section as one long scroll when JavaScript is off.
- **Sections and nav.** Each topic is a `<section class="topic" id="..."
  data-title="...">`. A small hash router builds the nav rail from DOM order and
  shows one section per `#id`; add a section and the nav updates itself.
- **The Audit Ledger.** Claims map to numbered prompts in the `AUDITS` array in
  the inline script. Cards render automatically, and `#audit-NN` deep links open
  and scroll to a specific audit.
- **Live widgets.** The cosmic odometer, the ticking fractional age, the
  grandparent clock (with adjustable assumption sliders), and the airline-remix
  map are all inline JS; the map is generated SVG with a simplified lower-48
  outline.
- **Anti-scraper email.** The contact address is assembled at view time in JS and
  never appears in the page source.

## Editing

- Copy style: sparing em dashes, no AI-writing tics, claims stay auditable.
- Photos live in `photos/`.
- Metadata in `<head>` assumes the canonical URL `https://datedavid.org/`.

## Deploying

Push to `main`. The site is served as static files (GitHub Pages).
