# datedavid.org

The source for [datedavid.org](https://datedavid.org/), a single-page, radically
transparent dating site. If you arrived here from the site's FAQ, this repository
is the receipts: every position on the page, every revision to it, and every
number behind it, timestamped in the commit log.

## The premise

The dating radius is two astronomical seconds: two seconds of the Sun's motion
relative to the cosmic microwave background, about 740 km or 460 miles. An
"airline remix" converts that distance into a wall-clock travel budget so any US
city reachable nonstop inside the same seven hours also qualifies. Around that
frame sits a full disclosure of the life plan: family size, the marriage
timeline, money, geography, health, dealbreakers, and an age range stated as a
function of family feasibility rather than taste.

Every factual claim is paired with an audit prompt the reader can paste into
any AI assistant. Nothing on the site asks to be taken on faith, and the site
says so.

## How it works

**One static file.** Everything is `index.html`: hand-written CSS, vanilla
JavaScript, no framework, no build step, and no dependency beyond Google Fonts.
`404.html` is the only other page; it redirects `/family`-style paths to
`/#family` and otherwise links home.

**Two layers.** The first section, Start Here, is the profile: hook, photo,
introduction, what dating him is like, what he's looking for, the essential
filters, and a low-stakes invitation. Every other section is the laboratory
behind it. Long arguments inside a section (the family-property math, the
optimal-stopping models, the full Shelf) sit in collapsed cards so the page
reads short first and deep on request.

**Sections and navigation.** Each topic is a
`<section class="topic" id="..." data-title="..." data-chapter="...">`. A hash
router shows one section per `#id` and builds the nav rail from DOM order. The
Contents page groups the sections into chapters from the `data-chapter`
attribute. Add a section, tag its chapter, and both update themselves.

**The Audit Ledger.** Claims map to numbered `{ title, claim, prompt }` entries in
the `AUDITS` array in the inline script. Cards render automatically and
`#audit-NN` deep links open and scroll to a card. Audit 00 is a static meta-audit
of the whole site. The placeholder `{{AGE}}` inside any prompt is replaced with
the author's live fractional age at the moment the prompt is copied, so the
copied text carries the age without the page stating a birthdate.

**Live widgets.** The cosmic odometer, the ticking fractional age, the grandparent
clock with adjustable assumption sliders, the age-range ceiling, the nine-month
chuppah date, and the airline-remix map are all inline JavaScript. The map is
generated SVG over a simplified lower-48 outline.

**Contact.** The email address is assembled at view time and never appears in the
page source. The video-call booking link is a prefilled `mailto:` built the same
way.

**No JavaScript.** A `<noscript>` block shows every section as one long scroll,
hides the empty nav rail, and explains that the clocks, the ledger, and the
contact address need scripting.

## Editing

The copy has house rules, and the test suite enforces most of them:

- Claims stay auditable. A new factual claim gets an audit card or a step in an
  existing one.
- Sparing em dashes in visible prose (a budget of sixteen outside the audit
  prompts), and none of the usual AI-writing tics; see `BANNED` in the tests.
- Counts written in prose must match the page: the number of dealbreakers, the
  number of sections named on the Questions page, the last audit number named
  in the Radius crosslink and the ledger subhead.
- Every section has a title and a chapter. Every internal link resolves. Every
  image has alt text and its file exists.
- The contact address never appears in the source of either page.

Photos live in `photos/` and are dated in their captions. Metadata in `<head>`
assumes the canonical URL `https://datedavid.org/`.

## Tests

```
python3 tests/check.py
```

Static checks need only Python 3 and Node. If Chrome is installed (or
`CHROME_BIN` points at one), the suite also renders the page headless and
checks that the router, the tickers, and the audit deep links work with no
JavaScript errors. The same script runs in GitHub Actions on every push.

## Deploying

Push to `main`. GitHub Pages serves the repository root as static files at the
`CNAME` domain.
