# BestKids V-School

A world-class Grade 5 homeschool curriculum: 36 weeks, five disciplines, built on Cambridge International, the Singapore Primary Mathematics syllabus and the Classical Trivium.

**Live site:** https://setopy.github.io/bestkids-vschool/

## What is here

- The full 36-week map (180 lessons planned) across Mathematics, Science, History & Geography, Literature and Languages.
- **Quarter 1 complete: Weeks 1–9, 45 full lessons.** Each has a big question, goals, core teaching, worked examples, a hands-on activity, practice with an answer key that explains *why*, a scholar's challenge, vocabulary and Socratic discussion questions.
- A parent guide with a weekly rhythm.
- Per-device progress tracking and a print layout (20pt body text).

## How it is built

Lessons are plain-text files in `content/`, one file per week. `build.py` turns them into the static site (no dependencies beyond Python 3).

```
python3 build.py
```

To add a lesson, copy the pattern of an existing one in `content/weekNN.txt`:

```
@lesson 10 math Fractional Equivalence
@hook The big question…
@goals
- …
@section Heading
Paragraph text with **bold** and *italic*.
| Table | Header |
| cell | cell |
%bar Label | part:2 | part ?:3
@example Question
- step
= answer
@activity Title | materials
- step
@practice
? question
= answer
! why
@challenge
? question
= answer
! why
@vocab
Term: definition
@talk
- discussion question
```

Then run `python3 build.py` and commit.

## Publishing

GitHub Pages serves the repository root of the `main` branch (Settings → Pages → Deploy from a branch → `main` / root).
