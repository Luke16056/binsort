# BinSort

Take one photo of a pile of rubbish and BinSort tells you which Irish bin each item goes in,
including "if clean / if dirty" advice. IS3329 Deliverable 2, Luke Delaney (124416056).

## What is in the code

Each folder is one box from the architecture diagram:

| Folder | Diagram box | Interface |
|---|---|---|
| `binsort/api/` (+ `templates/index.html`) | BinSort App + API | `GET /`, `POST /sort`, `POST /feedback` |
| `binsort/sorting/` | Sorting | `sort(photo)`, `sort_text(text)` |
| `binsort/photo_prep/` | Photo Prep | `prepare(photo)` |
| `binsort/item_detector/` | Item Detector (AI) + Vision AI | `detect(photo)`, `describe(text)` |
| `binsort/bin_rules/` | Bin Rules | `bin_for(item)` |
| `binsort/feedback/` | Feedback | `report(result, ok)` |
| `binsort/accounts/` | Accounts (deferred) | `login()`, `history()` (not built) |
| `binsort/database/` | Database | `Database` class + `bin_rules.csv` |

## Install (Windows)

You need Python 3.11 or newer.

```
cd binsort
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

On Mac or Linux use `python3 -m venv venv`, `source venv/bin/activate` and `cp .env.example .env`.

## Run

```
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Test

```
pytest
```

## Choosing the AI

Set `BINSORT_AI` in your `.env` file. This is the only setting to change to swap between AIs.

| `BINSORT_AI` | What happens |
|---|---|
| `fake` (default) | A fake AI that gives the same realistic answer for any photo. No internet or key needed. |
| `gemini` | The real Google Gemini vision model. Put your key in `GEMINI_API_KEY` (free key from https://aistudio.google.com). |
| `down` | A fake AI that always fails, to show the app falling back to typing. |

To switch to the real Gemini AI:

1. Get a free API key at https://aistudio.google.com ("Get API key").
2. In `.env`, set `BINSORT_AI=gemini` and paste the key after `GEMINI_API_KEY=`.
3. Stop the app (Ctrl+C) and start it again with `python app.py`.

`GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`, which answers in about 2 seconds.

The `.env` file is in `.gitignore`, so the API key is never committed.

Set `BINSORT_DEBUG=1` in `.env` to turn on Flask debug mode (auto-reload and the in-browser debugger) while changing the code. It is off by default.
