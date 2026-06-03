# ComplianceIQ — Intelligent Legal Compliance Assistant

Lightweight RAG stack using Google Gemini for generation and ChromaDB for embeddings.

Quick start

1. Create project folder and venv

```bash
python -m venv venv

venv\Scripts\activate

source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Google API key

4. Run backend (from `complianceiq` folder)

```bash
uvicorn app.main:app --reload
```

5. Run frontend (new terminal)

```bash
streamlit run frontend/streamlit_app.py
```
