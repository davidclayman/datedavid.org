#!/usr/bin/env python3
"""Integrity checks for datedavid.org's single-file site.

Static checks need only python3 + node. Set CHROME_BIN (or have Chrome at the
default macOS path) to also run the rendered smoke test.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
failures = []

def check(name, ok, detail=''):
    print(('PASS' if ok else 'FAIL'), name, ('- ' + detail if detail and not ok else ''))
    if not ok:
        failures.append(name)

s = open(HTML, encoding='utf-8').read()

# --- sections & internal links -------------------------------------------
sections = re.findall(r'<section class="topic" id="([a-z]+)" data-title="([^"]*)"', s)
ids = [i for i, _ in sections]
check('section ids unique', len(ids) == len(set(ids)))
check('every section has a title', all(t.strip() for _, t in sections))
chaptered = re.findall(r'<section class="topic" id="([a-z]+)" data-title="[^"]*" data-chapter="[^"]+"', s)
check('every section has a chapter', set(chaptered) == set(ids), f'missing: {sorted(set(ids) - set(chaptered))}')

audits_src = s.split('const AUDITS = [', 1)[1].split('\n  ];', 1)[0]
n_audits = len(re.findall(r'\n      title:', audits_src))
check('audit count sane', 10 <= n_audits <= 40, f'found {n_audits}')

valid = set(ids) | {f'audit-{i:02d}' for i in range(0, n_audits + 1)}  # 00 is the static meta-audit
hrefs = set(re.findall(r'href="#([a-zA-Z0-9-]+)"', s))
bad = hrefs - valid
check('internal links resolve', not bad, f'dangling: {sorted(bad)}')

# --- cross-referenced counts ---------------------------------------------
audits_sec = re.search(r'id="audits".*?</p>', s, re.S).group(0)
nums = [int(n) for n in re.findall(r'\b(\d{1,2})\b', audits_sec)]
check('ledger subhead names the last audit', nums and max(nums) == n_audits,
      f'subhead max {max(nums) if nums else None} vs {n_audits} audits')
m = re.search(r'runs 05–(\d+)', s)
check('radius crosslink names the last audit', m and int(m.group(1)) == n_audits)

WORDS = {'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12,
         'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16}
TENS = {'twenty': 20, 'thirty': 30, 'forty': 40}
ONES = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9}
def word_to_int(w):
    w = w.lower()
    if w in WORDS: return WORDS[w]
    if w in TENS: return TENS[w]
    a, _, b = w.partition('-')
    return TENS.get(a, 0) + ONES.get(b, 0) if a in TENS and b in ONES else None

# "Thirty-one sections about me" counts every section except Questions for You itself
m = re.search(r'([A-Z][a-z]+(?:-[a-z]+)?) sections about me is a monologue', s)
check('questions subhead counts the other sections', m and word_to_int(m.group(1)) == len(ids) - 1,
      f'subhead says {m.group(1) if m else "?"}, sections minus itself = {len(ids) - 1}')
db_sec = re.search(r'<section class="topic" id="dealbreakers".*?</section>', s, re.S).group(0)
db_main = db_sec.split('<h3', 1)[0]
n_db = db_main.count('<span class="k">')
m = re.search(r'These (\w+) are structural', s)
check('dealbreaker count matches subhead', m and WORDS.get(m.group(1)) == n_db,
      f'{n_db} items vs "These {m.group(1) if m else "?"}"')

# --- content invariants ---------------------------------------------------
check('email never in source', 'david@datedavid.org' not in s and 'mailto:david' not in s)
style = s.split('<style>', 1)[1].split('</style>', 1)[0]
bad_css = [l.strip() for l in style.splitlines() if 'content:' in l and '\\u' in l]
check('no \\u escapes in CSS content', not bad_css, str(bad_css))

BANNED = ['load-bearing', 'load bearing', 'delve', 'testament to', 'paradigm shift',
          "isn't just", 'not just about', 'game-chang', 'double-click on']
hits = [b for b in BANNED if b in s.lower()]
check('no banned phrases', not hits, str(hits))

# audit prompts may use em dashes; the visible prose keeps a budget
patent_src = s.split('<div class="body patent">', 1)[1].split('</details>', 1)[0] if '<div class="body patent">' in s else ''
n_dash = (s.count('\u2014') - audits_src.count('\u2014') - patent_src.count('\u2014')) + (s.count('\\u2014') - audits_src.count('\\u2014'))
check('em-dash budget outside audit prompts and the filing (<=16)', n_dash <= 16, f'found {n_dash}')

check('radius numbers consistent',
      '740&nbsp;km / 460&nbsp;miles' in s and '7 hours 4 minutes' in s
      and '5 hours 34 minutes' in s and '370&nbsp;km/s' in s)
check('no stale 230-mile radius', ' 230 mi' not in s and '≈370' not in s)
check('birthdate constant in both tickers', s.count('Date.UTC(1986, 2, 31') == 2)

# --- assets & accessibility ----------------------------------------------
imgs = re.findall(r'<img\b[^>]*>', s)
check('all images have alt text', all('alt="' in i for i in imgs))
srcs = re.findall(r'<img[^>]*src="(photos/[^"]+)"', s)
missing = [p for p in srcs if not os.path.exists(os.path.join(ROOT, p))]
check('image files exist', not missing, str(missing))
for sld in ('sldDelay', 'sldKids'):
    tag = re.search(r'<input[^>]*id="%s"[^>]*>' % sld, s)
    check(f'{sld} has aria-label', tag and 'aria-label' in tag.group(0))

# --- no-JS fallback and 404 ----------------------------------------------
check('noscript fallback shows sections', '<noscript>' in s and 'section.topic { display: block' in s)
nf = os.path.join(ROOT, '404.html')
check('404 page exists', os.path.exists(nf))
if os.path.exists(nf):
    n4 = open(nf, encoding='utf-8').read()
    check('404 links home', 'href="/"' in n4)
    check('404 is noindex', 'name="robots" content="noindex"' in n4)
    check('404 email never in source', 'david@' not in n4 and 'mailto:' not in n4)

# --- metadata -------------------------------------------------------------
for needle, name in [('property="og:image"', 'og:image'), ('property="og:title"', 'og:title'),
                     ('rel="canonical"', 'canonical'), ('name="description"', 'meta description'),
                     ('rel="icon"', 'favicon'), ('<title>', 'title tag')]:
    check(f'metadata: {name}', needle in s)

# --- javascript parses ----------------------------------------------------
js = s.split('<script>', 1)[1].rsplit('</script>', 1)[0]
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(js); jspath = f.name
r = subprocess.run(['node', '--check', jspath], capture_output=True, text=True)
check('javascript parses', r.returncode == 0, r.stderr[:300])
os.unlink(jspath)

# --- rendered smoke test (needs Chrome) ----------------------------------
chrome = os.environ.get('CHROME_BIN') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if os.path.exists(chrome) or os.environ.get('CHROME_BIN'):
    probe = s.replace('</body>', """<script>
window.__errs=[];window.onerror=(m)=>{__errs.push(String(m))};
window.addEventListener('load',()=>setTimeout(()=>{
  document.title=(__errs.length?('JSERR:'+__errs[0]):'JSOK')
    +'|tabs='+document.querySelectorAll('#navRail a').length
    +'|age='+(document.getElementById('age')||{}).textContent
    +'|a07='+(document.getElementById('audit-07')||{}).open;},400));
</script></body>""")
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, dir=ROOT, encoding='utf-8') as f:
        f.write(probe); ppath = f.name
    try:
        r = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--virtual-time-budget=4000', '--window-size=900,900',
                            '--dump-dom', 'file://' + ppath + '#audit-07'],
                           capture_output=True, text=True, timeout=90)
        title = re.search(r'<title>([^<]*)</title>', r.stdout)
        t = title.group(1) if title else ''
        check('smoke: no JS errors', t.startswith('JSOK'), t[:200])
        check('smoke: nav tab count matches sections', f'tabs={len(ids)}' in t, t[:200])
        check('smoke: age ticker runs', re.search(r'age=4\d\.\d{6}', t) is not None, t[:200])
        check('smoke: audit deep link opens card', 'a07=true' in t, t[:200])
    finally:
        os.unlink(ppath)
else:
    print('SKIP rendered smoke test (no Chrome found; set CHROME_BIN)')

print()
if failures:
    print(f'{len(failures)} FAILURE(S):', ', '.join(failures)); sys.exit(1)
print(f'all checks passed ({n_audits} audits, {len(ids)} sections, {n_db} dealbreakers)')
