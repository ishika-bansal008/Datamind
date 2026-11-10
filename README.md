# DataMind — Master Knowledge Workspace v3.0

A complete React + Vite website and FastAPI backend for turning raw notes, research, project lists and documents into structured knowledge, source-grounded key insights and exportable visual learning assets.

## What the application does

1. Accepts pasted raw text or PDF, DOCX, TXT, Markdown, CSV and JSON files.
2. Extracts readable source content on the backend. CSV and JSON arrays of objects are converted to tables; selectable-text PDF layout and DOCX tables are preserved where possible.
3. Extracts important words and important source lines independently from the language model. When the source is a detectable table or numbered project list, every extracted record contributes to the important-lines list.
4. Calls Google Gemini 3.8 Flash from the backend only. The browser never receives the API key.
5. Produces detailed Markdown analysis and 12 output formats: Flowchart, Mind Map, Structured Notes, Infographic, Timeline, Comparison Table, Step-by-Step Guide, Flashcards, Smart Summary, Workflow, Mermaid Diagram and Presentation.
6. Preserves parsed rows/items independently of the model response. If Gemini returns a short sample, the complete parsed source register and generated cards/diagram are still attached to the result.
7. Offers PNG and SVG downloads beside the actual diagram/card/table preview. Mermaid diagram export serializes the same rendered SVG shown on screen; card and table exports include the full collection, not only the visible scroll area.
8. Saves history, favorites and projects in the current browser's local storage.

## Important note about AI-generated images

Gemini 3.8 Flash returns text output, not generated image files. DataMind uses Gemini to understand and structure the source, then renders flowcharts, mind maps, timelines, cards and infographic/table layouts as vector SVG visuals in the website. These rendered visuals can be downloaded as SVG or rasterized PNG. The app does not claim that Gemini itself generated a photographic/raster image.

## Project structure

```text
DataMind-Master-Ultra-Pro-v3.0/
├── .github/workflows/deploy-frontend.yml
├── .gitignore
├── README.md
├── render.yaml
├── backend/
│   ├── .env.example
│   ├── Procfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── routes/health.py
│   │   ├── routes/transform.py
│   │   └── services/
│   │       ├── demo.py
│   │       ├── documents.py
│   │       ├── gemini.py
│   │       └── source_coverage.py
│   └── tests/
└── frontend/
    ├── .env.example
    ├── .env.production
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── styles.css
        ├── components/MermaidPreview.jsx
        ├── components/ResultPanel.jsx
        ├── data/formats.js
        ├── services/api.js
        └── utils/export.js
```

## Existing Render backend URL

The production frontend is preconfigured to call:

```text
https://datamind-e5zu.onrender.com
```

The frontend API client uses these routes:

- `GET /api/health`
- `POST /api/transform`
- `POST /api/transform/file`
- `POST /api/refine`

The deployed Render service could not be live-checked from the build environment. The package is configured for this URL and these route contracts; after deployment, open `https://datamind-e5zu.onrender.com/api/health` in a browser to verify the running service.

## Backend setup — local development

Use Python 3.11 or newer.

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and configure the key:

```bash
pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and set your own Google AI Studio key:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
AI_THINKING_LEVEL=low
```

Run the API from the `backend` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Local health endpoint: `http://127.0.0.1:8000/api/health`  
Interactive API docs: `http://127.0.0.1:8000/docs`

## Frontend setup — local development

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The development `.env.example` points to `http://localhost:8000`. Open `http://localhost:5173`.

For production builds, `frontend/.env.production` sets `VITE_API_URL` to the Render URL above. You can override it with a GitHub Actions repository variable named `VITE_API_URL`.

```bash
npm run build
npm run preview
```

## Render configuration for Gemini

In the existing Render Web Service for `datamind-e5zu.onrender.com`, open **Environment** and confirm these variables. Never put the Gemini key in frontend `.env`, GitHub Pages, or browser JavaScript.

```env
GEMINI_API_KEY=your_real_google_ai_studio_key
GEMINI_MODEL=gemini-3.8-flash
AI_THINKING_LEVEL=low
AI_MAX_SOURCE_CHARS=18000
AI_MAX_OUTPUT_TOKENS=3600
AI_ESTIMATED_TPM_BUDGET=7600
AI_MAX_RETRIES=0
AI_MIN_INTERVAL_SECONDS=1.5
AI_TIMEOUT_SECONDS=25
AI_FALLBACK_TO_DEMO=true
MAX_UPLOAD_MB=8
MAX_TEXT_CHARS=100000
RATE_LIMIT_PER_MINUTE=12
ALLOWED_ORIGINS=https://anup-prasad1408.github.io,http://localhost:5173,http://127.0.0.1:5173
```

`ALLOWED_ORIGINS` must contain the frontend's **origin only**, not its `/DataMind/` path. If your production frontend uses a different host, replace the GitHub Pages origin accordingly. After changing variables, save them and redeploy the Render service.

If you deploy the backend using this repository's `render.yaml` as a new Blueprint, set `GEMINI_API_KEY` as a secret when prompted. It is deliberately marked `sync: false` and is never committed.

## GitHub Pages deployment

1. Push the complete extracted project to the `main` branch of `Anup-Prasad1408/DataMind`.
2. In GitHub, open **Settings → Pages** and select **GitHub Actions** as the build/deployment source.
3. The included workflow installs frontend dependencies, builds Vite with `/DataMind/` as the base path and deploys `frontend/dist`.
4. The production API URL defaults to `https://datamind-e5zu.onrender.com`. Optionally add an Actions variable `VITE_API_URL` to override it.
5. Ensure Render's `ALLOWED_ORIGINS` includes `https://anup-prasad1408.github.io`.

## Detail, completeness and source integrity

- Default detail level is **Detailed**.
- Model prose is not treated as the only source of truth. A local parser extracts source rows first and attaches them to the result after AI generation.
- Tables and detectable project IDs are carried through to full-source views and relevant visual formats.
- Important words are extracted from source vocabulary; important lines come from source records or ranked original source sentences. The app does not present invented text as a quotation.
- If the file states an expected record count but the extracted text contains fewer records, the coverage section reports the mismatch. Missing rows are not fabricated.
- For scanned/image-only PDFs, OCR is not enabled. Use a selectable-text PDF or convert the source to DOCX/CSV/JSON/TXT first.

## Speed and quota behaviour

- `AI_THINKING_LEVEL=low` reduces additional reasoning work for these structured transformations.
- Identical requests are cached in-process for a short period.
- A busy AI slot or exceeded local token estimate fails fast to deterministic source-preserving output instead of making the user wait in a long queue.
- Transient API or quota errors can use the local fallback. This preserves extracted source records but does not reproduce full Gemini reasoning.
- Application token estimates and local pacing do not raise Google project TPM/RPM quotas. Check AI Studio for the actual project's quota and billing state.
- Render free instances can sleep while idle; their first request after inactivity may take longer while the service wakes.

## Tests

From the `backend` directory:

```bash
pytest -q
```

The included tests cover source coverage, important-line extraction, the supplied 25-project fixed-width layout fixture, fallback behaviour, CSV/JSON parsing, and visual/source-record completeness.

## Browser storage and privacy

Projects, favorites and history are saved in the current browser using local storage. They do not automatically sync between browsers or devices. The Gemini API key is only read by the Python backend environment.
