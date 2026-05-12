# Egyptian Constitution Mini-RAG Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-F9669A?style=flat&logo=qdrant&logoColor=white)

## About The Project

This project is a highly specialized **Retrieval-Augmented Generation (RAG)** system designed to query and analyze the Egyptian Constitution. Built with a strict Clean Architecture pattern, the system prioritizes legal accuracy and zero-hallucination responses. It utilizes advanced natural language processing to semantically search constitutional articles and generates precise, context-bound answers using state-of-the-art LLMs.

### Key Features
* **Smart Legal Chunking:** Custom Regex-based text splitting that perfectly isolates distinct constitutional articles (مواد) without arbitrary overlap, preserving legal integrity.
* **Cost-Effective Local Embeddings:** Utilizes `fastembed` with the `paraphrase-multilingual-MiniLM-L12-v2` model locally, ensuring zero API costs for vectorization, near-zero latency, and strict data privacy.
* **Dual LLM Support:** Implements the Factory Design Pattern to dynamically switch between **Google Gemini** and **Groq (Llama 3.1)** based on user preference.
* **Robust Data Layer:** Combines MongoDB (Document Store for raw data and metadata) with Qdrant (Vector Store for semantic search).

---

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                 │
│  ┌────────────────────────┐    ┌──────────────────────────────────┐     │
│  │  Streamlit UI          │    │  Any HTTP Client (curl, Postman) │     │
│  │  (app.py)              │    │                                  │     │
│  └────────┬───────────────┘    └──────────┬───────────────────────┘     │
│           │         HTTP Requests         │                             │
└───────────┼───────────────────────────────┼─────────────────────────────┘
            │                               │
┌───────────▼───────────────────────────────▼─────────────────────────────┐
│                         API LAYER (FastAPI)                             │
│  ┌────────────────────────┐  ┌────────────────────────────────────┐     │
│  │     routes/data.py     │  │           routes/nlp.py            │     │
│  │  POST upload/{id}      │  │  POST index/push/{id}              │     │
│  │  POST process/{id}     │  │  POST index/answer/{id}            │     │
│  └──────────┬─────────────┘  └─────────────────┬──────────────────┘     │
│             │                                  │                        │
└─────────────┼──────────────────────────────────┼────────────────────────┘
              │                                  │
┌─────────────▼──────────────────────────────────▼────────────────────────┐
│                      CONTROLLER LAYER                                   │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────────┐      │
│  │ DataController │  │ProcessController│ │   NlpController       │      │
│  │ (validate file)│  │ (regex chunking)│ │ (embed, search, RAG)  │      │
│  └────────────────┘  └────────────────┘  └───────────┬───────────┘      │
│                                                      │                  │
│  ┌────────────────┐  ┌───────────────────────────────┘                  │
│  │ FileController │  │                                                  │
│  │ (manage dirs/  │  │                                                  │
│  │  aiofiles)     │  │                                                  │
│  └────────────────┘  │                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      DATA LAYER (NoSQL)                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────────┐    │
│  │  ProjectModel  │  │  ChunkModel    │  │   DataBaseModel (base)  │    │
│  │  (projects CRUD)│ │  (chunks CRUD) │  │   (provides db_client)  │    │
│  └───────┬────────┘  └───────┬────────┘  └─────────────────────────┘    │
│          │                   │                                          │
│  ┌───────▼───────────────────▼────────┐                                 │
│  │          MongoDB (Motor async)     │                                 │
│  └────────────────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                     STORES LAYER (Factory Pattern)                      │
│                                                                         │
│  ┌─── LLM Store ──────────────────────────────────────────────────┐     │
│  │  LLMFactory → dynamically creates based on UI selection:       │     │
│  │    ├── GeminiProvider    (Google Gemini API)                   │     │
│  │    ├── GroqProvider      (Llama 3.1 via Groq API)              │     │
│  │    └── EmbeddingProvider (Local fastembed MiniLM)              │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌─── VectorDB Store ─────────────────────────────────────────────┐     │
│  │  VectorDBFactory → creates:                                    │     │
│  │    └── QdrantDB (Semantic Vector Search & Storage)             │     │
│  └────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
