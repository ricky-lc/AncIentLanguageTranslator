# Ancient Language Translator

Lightweight translator app for converting:
- **English/Italian → Ancient Language**
- **Ancient Language → English**

It includes a browser UI, an HTTP API, and translation logic implemented in both Python and Node.js.

## What this project is about

This project provides fast dictionary-based translation with practical language handling:
- Automatic **English vs Italian** input detection
- Optional manual source language selection
- Support for common words and connectors (for better sentence coverage)
- Basic handling for contractions and gerund forms
- Reverse translation from Ancient Language to English
- Translation coverage metadata (`mappedTerms`, `totalTerms`, `coverage`)

## Tech stack

- **Backend runtime (default):** Python 3 (`http.server`)
- **Alternative backend files present:** Node.js (HTTP server + API handler)
- **Frontend:** Vanilla HTML/CSS/JavaScript (`index.html`)
- **Tests:**  
  - Python `unittest` (in `tests/`)  
  - Node test runner (`node --test`, in `test/`)
- **Data source:** `vocabulary.json`

## Repository structure

- `/backend/server.py` — main server started by `npm start`
- `/backend/translator.py` — Python translation engine
- `/src/translator.js` — Node translation engine
- `/api/translate.js` — Node API handler
- `/index.html` — UI (served at `/`)
- `/tests/test_translator.py` — Python test suite
- `/test/translator.test.js` — Node test suite
- `/vocabulary.json` — vocabulary data used to build dictionaries

## Local setup

### Requirements

- Python 3.9+ (or any modern Python 3)
- Node.js 18+ (defined in `package.json`)
- npm

### Install

No additional dependencies are required.

```bash
npm install
```

## Run locally

Start the app:

```bash
npm start
```

This launches the Python server at:
- `http://localhost:3000`

Open the URL in your browser and use the translator UI.

## Local testing

Run all tests (Python + Node):

```bash
npm test
```

Equivalent command from `package.json`:
- `python -m unittest discover -s tests -p 'test_*.py' && node --test`

## API usage

### Endpoint

- `POST /api/translate`

### Request body

```json
{
  "text": "if fire isn't water",
  "direction": "to_ancient",
  "sourceLanguage": "auto"
}
```

### Fields

- `text` *(string)*: input to translate
- `direction` *(string)*:
  - `to_ancient` (default)
  - `from_ancient`
- `sourceLanguage` *(string, for `to_ancient`)*:
  - `auto` (default)
  - `english`
  - `italian`

### Response example

```json
{
  "translation": "ef brisingr er néiat deloi",
  "sourceLanguage": "english",
  "mappedTerms": 5,
  "totalTerms": 5,
  "coverage": 1
}
```

## Notes

- The project is dictionary-based and rule-assisted (not ML-based).
- Coverage depends on `vocabulary.json` and built-in essential additions.
- Unknown terms are preserved in output when no mapping is found.
