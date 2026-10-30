# SmartBudget JA - Group 20

Streamlit budgeting prototype with the original navy/neon app styling, dark mode, receipt capture, knowledge base, Ask SmartBudget and calculated insights.

## Deploy on Streamlit Community Cloud
- Repository: JILLYBOOHOO/group20samartbudgetapp
- Branch: main
- Main file: cloud_app.py
- Python: 3.12 recommended

requirements.txt installs the Python dependencies. packages.txt installs Tesseract OCR and Poppler on Linux. No API key is required.

Each visitor starts with their own temporary copy of the fictional records in demo_data/. The initial reporting month matches those records. Edits are session-local, do not update GitHub, and are not guaranteed to persist after a session ends or the server restarts. Export records before leaving.

## Local development
    python -m pip install -r requirements.txt
    python -m streamlit run app.py

Local app.py writes durable records to data/ (ignored by Git). The public demo uses cloud_app.py instead. On Windows, OCR uses the included Windows adapter. Browser camera permission is required for capture; JPG/PNG upload is also supported.

## Features
- Dashboard totals, category charts, spending pace, budgets and savings goals.
- Multiple dated income and expense records, ledger filters and CSV export.
- Receipt photo capture/upload and text extraction, followed by review before saving.
- PDF, TXT and CSV document imports.
- Searchable, editable knowledge entries and keyword-based Ask SmartBudget answers.
- Explainable insights calculated from recorded transactions, budgets and goals.

## Demo data and limitations
All committed sample financial records were confirmed fictional by the project owner. These include salary/freelance income, example expenses, a monthly budget and a Christmas savings goal. The app has no live bank connection and no external generative-AI service. Available balance is recorded income minus expenses, not an actual bank balance. OCR and word matching can make mistakes. Uploaded images/documents are processed by the machine hosting the app. Use fictional information on the public deployment.

## Tests
    python -m pytest tests -q
