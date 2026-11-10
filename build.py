#!/usr/bin/env python3
"""BestKids V-School site generator.

Reads lesson files from content/*.txt and writes a static site (index.html,
weeks/, lessons/, guide.html) that GitHub Pages serves directly.

Run:  python3 build.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "BestKids V-School"

SUBJECTS = {
    "math": ("Mathematics", "∑"),
    "science": ("Science", "⚛"),
    "history": ("History & Geography", "🏛"),
    "literature": ("Literature", "✒"),
    "languages": ("Languages", "Ω"),
}
ORDER = list(SUBJECTS)

QUARTERS = [
    ("Quarter 1", "Foundations", 1, 9),
    ("Quarter 2", "Structure", 10, 18),
    ("Quarter 3", "Connection", 19, 27),
    ("Quarter 4", "Mastery", 28, 36),
]

MAP = {
    "math": """Non-Decimal Bases|Divisibility & Primes|Order of Operations|Bar Modeling I: Part-Whole|Bar Modeling II: Multi-Step|Cryptarithms|Sequences|Variables|Q1 Synthesis|Fractional Equivalence|Adding & Subtracting Fractions|Fraction Multiplication (Area Models)|Fraction Division (Reciprocals)|Fraction Word Problems|Decimal Place Value|Decimal Operations (Powers of 10)|Measurement Conversions|Multi-Step Integration|Ratios (Part-to-Part & Part-to-Whole)|Complex Ratios|Unit Rates|Kinematics (Distance, Rate, Time)|Percentages & Conversions I|Percentages & Conversions II|Finding the Base, Rate and Part|Successive Discounts|Competition Math|Angle Chasing|Area & Perimeter (Composite Shapes)|3D Surface Area & Volume|The Coordinate Plane|Data Analysis|Systematic Counting & Combinatorics|Probability|Real-World Modeling|AMC 8 Capstone""",
    "science": """Metrology & SI Units|Particle Theory|Atomic Structure & the Bohr Model|The Periodic Table|Molecular Bonds|Chemical vs Physical Change|Separation Techniques|The pH Scale|Experiment Design|Conservation of Energy|Thermodynamics: Conduction, Convection, Radiation|Newton's Laws|Applied Forces|Simple Machines|Wave Mechanics|The Electromagnetic Spectrum|Circuits|Engineering Challenge|Earth's Spheres|Atmospheric Mechanics|Meteorology & Weather|The Water Cycle|Geology & Plate Tectonics|Orbital Mechanics|Earth's Tilt & the Seasons|Space Exploration|Atmospheric Data Project|Cell Theory|Microorganisms|Plant Physiology|Human Anatomy I|Human Anatomy II|Genetics & Heredity|Ecosystems & Food Webs|Environmental Science|Research Symposium""",
    "history": """Cartography & Map Projections|Topography|Biomes|Hydrology|The Agricultural Revolution|Mesopotamia|Ancient Egypt|The Indus Valley|Geographic Determinism|Ancient China & the Mandate of Heaven|Hammurabi's Code|The Phoenicians|Greece I: Athens|Greece II: Sparta|The Persian Empire|Alexander the Great|Herodotus|The Ethics of Empire|The Roman Republic|The Roman Empire|Roman Engineering|The Han Dynasty|The Silk Road I|The Silk Road II|Mauryan & Gupta Empires|The Fall of Rome|Mapping Trade|The Byzantine Empire|The Islamic Golden Age|Feudalism in Europe & Japan|The Mongol Empire|The Kingdom of Mali|Mesoamerican Engineering|The Aztec & Inca|The Age of Discovery|Architect of Civilization Project""",
    "literature": """Active Reading|The Hero's Journey|Greek & Roman Myth|Norse Myth|Fables & Aesop|Oral Tradition|Protagonists|Setting as Character|Comparative Myth|Plot Anatomy|Point of View|The Unreliable Narrator|Conflict Typology|Subtext & Dialogue|Theme|Tone vs Mood|Historical Fiction|Literary Analysis Paper|Poem Anatomy & Meter|Figurative Language I|Figurative Language II|Sonic Devices|Classical Forms: Sonnet & Blank Verse|Rhetoric: Ethos, Pathos, Logos|Logical Fallacies|Oratory Analysis|Declamation|Allegory|Utopia & Dystopia|Satire & Irony|Societal Structures|Cross-Textual Synthesis|Literary Criticism|Capstone Drafting|Capstone Typesetting|Socratic Defense""",
    "languages": """The Indo-European Tree|Phonetics|Morphology 101|Latin & Greek Number Roots I|Latin & Greek Number Roots II|French Immersion I: Greetings|French Immersion II: Family & Numbers|French Immersion III: Daily Life|Etymology Mapping|Classical Roots: Geo|Classical Roots: Bio|Classical Roots: Astro|Latin Declensions|French: Navigation I|French: Navigation II|French: Environment|Idiomatic Translation|Scientific Translation|Classical Roots: Logic|Classical Roots: Time|Classical Roots: Governance|Advanced Prefixes I|Advanced Prefixes II|French: Past Tense I|French: Past Tense II|French: Storytelling|Logical Argumentation|STEM & Medical Roots|Tech & Physics Roots|The Latin Legal Tradition|Classical Allusions|French: Commerce I|French: Commerce II|French: Negotiation|Bilingual Decoder I|Bilingual Decoder II""",
}
MAP = {k: v.split("|") for k, v in MAP.items()}
for k, v in MAP.items():
    assert len(v) == 36, (k, len(v))


def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


# ---------------------------------------------------------------- parsing
def parse(path):
    lessons, cur, block = [], None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("@lesson "):
            _, week, subj, title = line.split(" ", 3)
            cur = dict(week=int(week), subject=subj, title=title, hook="", goals=[],
                       sections=[], examples=[], activity=None, practice=[],
                       challenge=None, vocab=[], talk=[])
            lessons.append(cur)
            block = None
            continue
        if cur is None or not line.strip():
            continue
        if line.startswith("@"):
            key, _, rest = line[1:].partition(" ")
            rest = rest.strip()
            if key == "hook":
                cur["hook"] = rest
                block = None
            elif key == "section":
                block = ("section", dict(h=rest, body=[]))
                cur["sections"].append(block[1])
            elif key == "example":
                block = ("example", dict(q=rest, steps=[], a=""))
                cur["examples"].append(block[1])
            elif key == "activity":
                title, _, mat = rest.partition("|")
                block = ("activity", dict(title=title.strip(), materials=mat.strip(), steps=[]))
                cur["activity"] = block[1]
            elif key in ("goals", "practice", "challenge", "vocab", "talk"):
                block = (key, None)
            else:
                raise ValueError(f"{path.name}: unknown directive @{key}")
            continue
        kind = block[0] if block else None
        t = line.strip()
        if kind == "goals":
            cur["goals"].append(t.lstrip("- "))
        elif kind == "talk":
            cur["talk"].append(t.lstrip("- "))
        elif kind == "section":
            block[1]["body"].append(t)
        elif kind == "example":
            if t.startswith("= "):
                block[1]["a"] = t[2:]
            else:
                block[1]["steps"].append(t.lstrip("- "))
        elif kind == "activity":
            block[1]["steps"].append(t.lstrip("- "))
        elif kind in ("practice", "challenge"):
            if t.startswith("? "):
                item = dict(q=t[2:], a="", why="")
                if kind == "practice":
                    cur["practice"].append(item)
                else:
                    cur["challenge"] = item
            else:
                item = cur["practice"][-1] if kind == "practice" else cur["challenge"]
                if t.startswith("= "):
                    item["a"] = t[2:]
                elif t.startswith("! "):
                    item["why"] = t[2:]
                else:
                    raise ValueError(f"{path.name}: bad practice line: {t}")
        elif kind == "vocab":
            term, _, d = t.partition(": ")
            cur["vocab"].append((term, d))
        else:
            raise ValueError(f"{path.name}: stray line: {t}")
    return lessons


def render_body(lines):
    """Paragraphs, tables (| a | b |), bullet lists (- x) and bar models (%bar)."""
    out, i = [], 0
    while i < len(lines):
        t = lines[i]
        if t.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            head, *rest = rows
            out.append("<div class='tablewrap'><table><thead><tr>" +
                       "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest) +
                       "</tbody></table></div>")
        elif t.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif t.startswith("%bar "):
            parsed = []
            while i < len(lines) and lines[i].startswith("%bar "):
                label, *segs = [p.strip() for p in lines[i][5:].split("|")]
                parsed.append((label, [(seg.rpartition(":")[0], float(seg.rpartition(":")[2])) for seg in segs]))
                i += 1
            widest = max(sum(u for _, u in segs) for _, segs in parsed)
            rows = []
            for label, segs in parsed:
                cells = "".join(
                    f"<span class='seg{' q' if '?' in text else ''}' style='flex:{units:g}'>{inline(text)}</span>"
                    for text, units in segs)
                width = 100 * sum(u for _, u in segs) / widest
                rows.append(f"<div class='barrow'><span class='barlabel'>{inline(label)}</span>"
                            f"<div class='barspace'><div class='bar' style='width:{width:.1f}%'>{cells}</div></div></div>")
            out.append("<figure class='barmodel'>" + "".join(rows) + "</figure>")
        else:
            out.append(f"<p>{inline(t)}</p>")
            i += 1
    return "\n".join(out)


# ---------------------------------------------------------------- pages
def page(title, body, depth=0, cls=""):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="A world-class Grade 5 curriculum: 36 weeks of mathematics, science, history, literature and languages.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="manifest" href="{up}manifest.webmanifest">
<meta name="theme-color" content="#0f1b33">
<link rel="icon" type="image/png" href="{up}assets/icons/icon-192.png">
<link rel="apple-touch-icon" href="{up}assets/icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="BestKids">
</head>
<body class="{cls}">
<header class="top">
  <a class="brand" href="{up}index.html"><span class="crest">B</span><span>BestKids <em>V-School</em></span></a>
  <nav><button class="install" data-install hidden>Install app</button><a href="{up}index.html#map">Curriculum</a><a href="{up}guide.html">Parent guide</a></nav>
</header>
{body}
<footer class="foot">
  <p><strong>BestKids V-School</strong> · Grade 5 · Built on Cambridge International, Singapore Primary Mathematics and the Classical Trivium.</p>
  <p class="small">Ask why. Show your working. Check your answer.</p>
</footer>
<script>window.SW_PATH="{up}sw.js";</script>
<script src="{up}assets/app.js"></script>
</body>
</html>
"""


def lid(l):
    return f"w{l['week']:02d}-{l['subject']}"


def lesson_page(l, prev, nxt):
    name, icon = SUBJECTS[l["subject"]]
    b = [f"""<main class="lesson subj-{l['subject']}" data-lesson="{lid(l)}">
<div class="crumbs"><a href="../index.html#map">Curriculum</a> › <a href="../weeks/week-{l['week']:02d}.html">Week {l['week']}</a> › {name}</div>
<div class="lhead">
  <span class="badge">{icon} {name} · Week {l['week']}</span>
  <h1>{inline(l['title'])}</h1>
  <blockquote class="hook"><span>The big question</span>{inline(l['hook'])}</blockquote>
</div>
<section class="goals"><h2>By the end of this lesson you will be able to</h2><ol>"""]
    b += [f"<li>{inline(g)}</li>" for g in l["goals"]]
    b.append("</ol></section>")
    for n, s in enumerate(l["sections"], 1):
        b.append(f"<section class='core'><h2><span class='num'>{n}</span>{inline(s['h'])}</h2>{render_body(s['body'])}</section>")
    if l["examples"]:
        b.append("<section class='examples'><h2>Worked examples</h2><p class='hint'>Cover the steps. Predict each line before you read it.</p>")
        for n, e in enumerate(l["examples"], 1):
            b.append(f"<div class='ex'><h3>Example {n}</h3><p class='exq'>{inline(e['q'])}</p><ol>" +
                     "".join(f"<li>{inline(s)}</li>" for s in e["steps"]) +
                     f"</ol><p class='exa'><strong>Answer:</strong> {inline(e['a'])}</p></div>")
        b.append("</section>")
    a = l["activity"]
    if a:
        b.append(f"<section class='activity'><h2>Hands-on: {inline(a['title'])}</h2>" +
                 (f"<p class='materials'><strong>You need:</strong> {inline(a['materials'])}</p>" if a["materials"] else "") +
                 "<ol>" + "".join(f"<li>{inline(s)}</li>" for s in a["steps"]) + "</ol></section>")
    if l["practice"]:
        b.append("<section class='practice'><div class='phead'><h2>Practice</h2>"
                 "<button class='ghost' data-toggle-answers>Show all answers</button></div>"
                 "<p class='hint'>Write your full working in your notebook before opening an answer.</p><ol class='qs'>")
        for p in l["practice"]:
            b.append(f"<li><p>{inline(p['q'])}</p><details><summary>Answer and why</summary>"
                     f"<p><strong>{inline(p['a'])}</strong></p><p class='why'><span>Why</span>{inline(p['why'])}</p></details></li>")
        b.append("</ol></section>")
    c = l["challenge"]
    if c:
        b.append(f"<section class='challenge'><h2>★ Scholar's challenge</h2><p>{inline(c['q'])}</p>"
                 f"<details><summary>Answer and why</summary><p><strong>{inline(c['a'])}</strong></p>"
                 f"<p class='why'><span>Why</span>{inline(c['why'])}</p></details></section>")
    if l["vocab"]:
        b.append("<section class='vocab'><h2>Words to own</h2><dl>" +
                 "".join(f"<div><dt>{inline(t)}</dt><dd>{inline(d)}</dd></div>" for t, d in l["vocab"]) + "</dl></section>")
    if l["talk"]:
        b.append("<section class='talk'><h2>Socratic table talk</h2><p class='hint'>Discuss aloud. There is no answer key: defend your thinking with reasons.</p><ul>" +
                 "".join(f"<li>{inline(t)}</li>" for t in l["talk"]) + "</ul></section>")
    b.append("<section class='done'><button class='primary' data-complete>Mark lesson complete</button>"
             "<button class='ghost' onclick='window.print()'>Print this lesson</button></section>")
    nav = "<nav class='pn'>"
    nav += f"<a href='{lid(prev)}.html'>← {esc(prev['title'])}</a>" if prev else "<span></span>"
    nav += f"<a href='{lid(nxt)}.html'>{esc(nxt['title'])} →</a>" if nxt else "<span></span>"
    b.append(nav + "</nav></main>")
    return page(f"{l['title']} · Week {l['week']} {name} · {SITE}", "\n".join(b), 1)


def week_page(w, by_id):
    q = next(q for q in QUARTERS if q[2] <= w <= q[3])
    b = [f"""<main class="week"><div class="crumbs"><a href="../index.html#map">Curriculum</a> › {q[0]}</div>
<h1>Week {w}</h1><p class="lede">Five lessons. One per subject. Work in order or follow your timetable.</p><div class="cards">"""]
    for s in ORDER:
        name, icon = SUBJECTS[s]
        title = MAP[s][w - 1]
        l = by_id.get(f"w{w:02d}-{s}")
        if l:
            b.append(f"<a class='card subj-{s}' data-lesson='{lid(l)}' href='../lessons/{lid(l)}.html'><span class='badge'>{icon} {name}</span>"
                     f"<h3>{esc(l['title'])}</h3><p>{inline(l['hook'])}</p><span class='go'>Open lesson →</span></a>")
        else:
            b.append(f"<div class='card soon subj-{s}'><span class='badge'>{icon} {name}</span><h3>{esc(title)}</h3><p>Lesson in preparation.</p></div>")
    b.append("</div><nav class='pn'>")
    b.append(f"<a href='week-{w-1:02d}.html'>← Week {w-1}</a>" if w > 1 else "<span></span>")
    b.append(f"<a href='week-{w+1:02d}.html'>Week {w+1} →</a>" if w < 36 else "<span></span>")
    b.append("</nav></main>")
    return page(f"Week {w} · {SITE}", "\n".join(b), 1)


def index_page(by_id):
    ready = len(by_id)
    b = [f"""<section class="hero">
  <p class="eyebrow">Grade 5 · 36 weeks · 5 disciplines</p>
  <h1>A world-class education,<br>built at home.</h1>
  <p class="lede">A complete Grade 5 programme drawn from Cambridge International, the Singapore Primary Mathematics syllabus and the Classical Trivium. Every lesson begins with a question, builds real understanding, and ends with work you can defend.</p>
  <div class="cta"><a class="primary" href="#map">Open the curriculum</a><a class="ghost" href="guide.html">How to teach it</a></div>
  <div class="stats"><div><b>180</b><span>lessons planned</span></div><div><b>{ready}</b><span>lessons ready</span></div><div><b id="donecount">0</b><span>completed by you</span></div></div>
</section>
<section class="pillars">
  <div><h3>Ask why</h3><p>Each lesson opens with a big question. Understanding comes before procedure.</p></div>
  <div><h3>Show your working</h3><p>Worked examples model the reasoning line by line, the way a mathematician defends a proof.</p></div>
  <div><h3>Check your answer</h3><p>Every answer key explains why the answer is right, so mistakes turn into lessons.</p></div>
  <div><h3>Speak and defend</h3><p>Socratic table talk trains the scholar to argue clearly and listen carefully.</p></div>
</section>
<section id="map" class="map"><h2>The 36-week map</h2>
<div class="legend">""" + "".join(f"<span class='subj-{s}'><i></i>{SUBJECTS[s][0]}</span>" for s in ORDER) + "</div>"]
    for qn, theme, a, z in QUARTERS:
        b.append(f"<div class='quarter'><div class='qhead'><h3>{qn}</h3><span>{theme} · Weeks {a}–{z}</span></div><div class='weeks'>")
        for w in range(a, z + 1):
            live = any(f"w{w:02d}-{s}" in by_id for s in ORDER)
            b.append(f"<a class='wk{'' if live else ' soon'}' href='weeks/week-{w:02d}.html' data-week='{w}'><div class='wkn'>Week {w}<em>{'' if live else 'in preparation'}</em></div><ul>")
            for s in ORDER:
                b.append(f"<li class='subj-{s}' data-lesson='w{w:02d}-{s}'><i></i>{esc(MAP[s][w-1])}</li>")
            b.append("</ul></a>")
        b.append("</div></div>")
    b.append("</section>")
    return page(f"{SITE} · Grade 5 World-Class Curriculum", "\n".join(b), 0, "home")


GUIDE = """<main class="lesson guide">
<h1>Parent guide</h1>
<p class="lede">How to run BestKids V-School at home, in about three focused hours a day.</p>
<section class="core"><h2><span class="num">1</span>The weekly rhythm</h2>
<p>Each week has five lessons, one per discipline. A lesson is designed for 45 to 60 minutes of teaching and discussion, followed by independent practice.</p>
<div class="tablewrap"><table><thead><tr><th>Day</th><th>Morning block</th><th>Second block</th><th>Afternoon</th></tr></thead><tbody>
<tr><td>Monday</td><td>Mathematics lesson</td><td>Literature lesson</td><td>Reading (30 min)</td></tr>
<tr><td>Tuesday</td><td>Science lesson</td><td>Maths practice</td><td>Hands-on activity</td></tr>
<tr><td>Wednesday</td><td>History lesson</td><td>Languages lesson</td><td>Reading (30 min)</td></tr>
<tr><td>Thursday</td><td>Maths challenge</td><td>Science or history activity</td><td>Writing</td></tr>
<tr><td>Friday</td><td>Review of all five</td><td>Socratic table talk</td><td>Free project</td></tr>
</tbody></table></div></section>
<section class="core"><h2><span class="num">2</span>How each lesson is built</h2>
<ul><li><strong>The big question.</strong> Read it aloud and wait. Let your child guess before you teach.</li>
<li><strong>Core ideas.</strong> Read together. Stop at every bold word and ask your child to explain it back.</li>
<li><strong>Worked examples.</strong> Cover the steps with a sheet of paper and reveal one line at a time.</li>
<li><strong>Hands-on.</strong> Real objects first. The abstract idea sticks when the hands have met it.</li>
<li><strong>Practice.</strong> Full working in a notebook. Open the answer only after a real attempt, and always read the <em>why</em>.</li>
<li><strong>Scholar's challenge.</strong> Harder than grade level on purpose. Struggle here is the goal, not a failure.</li>
<li><strong>Socratic table talk.</strong> Open questions with no answer key. Ask "what is your reason?" often.</li></ul></section>
<section class="core"><h2><span class="num">3</span>The scholar's notebooks</h2>
<p>Keep one bound notebook per discipline. Date every page. Never erase a mistake: draw one line through it and write the correction beside it. At the end of each quarter the notebooks are the portfolio.</p></section>
<section class="core"><h2><span class="num">4</span>Mastery before speed</h2>
<p>Move on when your child can teach the idea back to you without the page. If a lesson needs two days, give it two days. The Singapore approach moves from concrete objects, to pictures, to symbols. If the symbols are shaky, go back to the objects.</p></section>
<section class="core"><h2><span class="num">5</span>Install it as an app</h2>
<p>BestKids V-School can be installed and then works without internet. On Android or a computer (Chrome or Edge), press <strong>Install app</strong> in the top bar, or choose "Install" from the browser menu. On iPhone or iPad, open the site in Safari, tap <strong>Share</strong>, then <strong>Add to Home Screen</strong>. Open the app once while online so every lesson is saved to the device.</p></section>
<section class="core"><h2><span class="num">6</span>Tracking progress</h2>
<p>Press <strong>Mark lesson complete</strong> at the end of a lesson. The curriculum map then shows a tick for that lesson. Progress is stored in the browser on that device only.</p></section>
</main>"""


MANIFEST = """{
  "name": "BestKids V-School",
  "short_name": "BestKids",
  "description": "A world-class Grade 5 curriculum: 36 weeks, five disciplines.",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "background_color": "#fbf8f1",
  "theme_color": "#0f1b33",
  "icons": [
    {"src": "assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
    {"src": "assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
  ]
}
"""

SW = """// Generated by build.py. Do not edit by hand.
const CACHE = 'bestkids-%(version)s';
const FILES = %(files)s;

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Network first, so new lessons appear as soon as you are online; cache when offline.
// Only this site's own files are handled. Web fonts are left to the browser, and
// the pages fall back to built-in fonts when offline.
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== self.location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return res;
      })
      .catch(() => caches.match(e.request, {ignoreSearch: true}).then((hit) => hit || (e.request.mode === 'navigate' ? caches.match('./index.html') : Response.error())))
  );
});
"""


def write_pwa():
    import hashlib
    import json
    files = ["./", "index.html", "guide.html", "manifest.webmanifest", "assets/style.css", "assets/app.js"]
    files += sorted(str(p.relative_to(ROOT)) for d in ("lessons", "weeks", "assets/icons") for p in (ROOT / d).glob("*"))
    digest = hashlib.sha1(SW.encode())
    for f in files[1:]:
        if f != "manifest.webmanifest":
            digest.update((ROOT / f).read_bytes())
    (ROOT / "manifest.webmanifest").write_text(MANIFEST, encoding="utf-8")
    (ROOT / "sw.js").write_text(SW % dict(version=digest.hexdigest()[:10], files=json.dumps(files, indent=1)), encoding="utf-8")


def main():
    lessons = []
    for f in sorted((ROOT / "content").glob("*.txt")):
        lessons += parse(f)
    lessons.sort(key=lambda l: (l["week"], ORDER.index(l["subject"])))
    by_id = {lid(l): l for l in lessons}
    assert len(by_id) == len(lessons), "duplicate lesson id"
    (ROOT / "lessons").mkdir(exist_ok=True)
    (ROOT / "weeks").mkdir(exist_ok=True)
    for old in (ROOT / "lessons").glob("*.html"):
        old.unlink()
    for i, l in enumerate(lessons):
        prev = lessons[i - 1] if i else None
        nxt = lessons[i + 1] if i + 1 < len(lessons) else None
        (ROOT / "lessons" / f"{lid(l)}.html").write_text(lesson_page(l, prev, nxt), encoding="utf-8")
    for w in range(1, 37):
        (ROOT / "weeks" / f"week-{w:02d}.html").write_text(week_page(w, by_id), encoding="utf-8")
    (ROOT / "index.html").write_text(index_page(by_id), encoding="utf-8")
    (ROOT / "guide.html").write_text(page(f"Parent guide · {SITE}", GUIDE, 0), encoding="utf-8")
    (ROOT / ".nojekyll").write_text("")
    write_pwa()
    print(f"built {len(lessons)} lessons")


if __name__ == "__main__":
    main()
