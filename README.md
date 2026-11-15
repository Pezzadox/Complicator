# The Complicator

**Making maths harder, so it's easier.**

A calculator that does the opposite of a calculator. Type an easy sum, like `1 + 1`, and the Complicator turns it into a chain of steps that all land on the same answer. You work through every step to unlock it.

Built for neurodivergent brains (ADHD, autism, dyscalculia and more). A plain sum is boring, and boredom is where attention drops. A chain of small wins holds it.

Idea by King of Ink.

## How it works

- **Big chunky calculator.** Big buttons, big screen, high contrast.
- **Puzzle box.** A small screen over the corner of the main one (like a WhatsApp video call) showing the step you're on.
- **Dimension stack.** Tiers like a 3D chess board, one per step. Chill = 2D, Tricky = 4D, Chaos = 8D.

## Built for ADHD

- **Jump between tasks:** three puzzle tabs (A, B, C) that each keep their progress.
- **Hyperfocus:** Flow mode loads the next puzzle by itself, plus a streak counter and focus timer.
- **Never stuck:** a miss gets "have another go", then a hint, then the answer to type in. No red crosses.
- **New way:** a different route to the same answer.
- **Surprise:** makes up a sum for you.
- **Focus view:** only the current step.
- **Break nudge:** after 15, 25 or 45 minutes, with a 5-minute break timer.
- **Comfort settings:** calm colours, bigger text, easy-read font, buzz on correct answers, read steps aloud.
- Progress is saved in the browser.

## Run it

It's one file. Open `index.html` in any browser, or host it on GitHub Pages (Settings → Pages → deploy from `main`).

Keyboard: numbers and `+ - * /`, Enter for `=`, Backspace to delete, `h` for a hint, `s` for surprise, `[` and `]` to switch puzzles.

## Tests

```
pip install playwright && playwright install chromium
python tests/test_app.py
```

Checks the puzzle maths (16,000+ random chains), a full play-through, hints, puzzle tabs, flow mode, saving, settings, the break nudge, and layouts on five phone sizes.
