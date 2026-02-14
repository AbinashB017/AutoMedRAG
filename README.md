# AutoMedRAG

A medical document retrieval and analysis system using FastAPI, FAISS, and LLMs for evidence-based medical question answering.

## Features

- 🔍 **PubMed Integration**: Direct access to 35M+ medical articles
- 🧠 **Hybrid Retrieval**: Combines semantic (dense) and keyword (sparse) search
- 📊 **Smart Re-ranking**: Cross-encoder model for relevance scoring
- 🤖 **LLM-Powered Answers**: Generate evidence-based responses using NVIDIA endpoints
- 📚 **Structured Output**: Formatted answers with cited sources

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env  # Configure your NVIDIA_API_KEY
```

## Running the Backend

```bash
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Architecture

Query → PubMed Search → Hybrid Retrieval (Dense + BM25) → Re-ranking → LLM Generation → Answer + Papers

## Technologies

FastAPI • Sentence Transformers • FAISS • BM25 • Cross-Encoder • NVIDIA LLM

```
automedrag/
├── backend/
│   ├── main.py
│   ├── services/
│   │   ├── pubmed_service.py
│   │   ├── retrieval_service.py
│   │   ├── reranker_service.py
│   │   └── llm_service.py
│   ├── models/
│   │   └── schemas.py
│   └── utils/
│       └── config.py
├── frontend/
│   └── app.py
├── requirements.txt
└── README.md
```

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the backend:
```bash
python backend/main.py
```

Run the frontend:
```bash
python frontend/app.py
```
