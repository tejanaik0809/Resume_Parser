# GenAI Resume Parser

This project is a web-based resume parsing system that automatically extracts structured information from PDF and DOCX resumes. It leverages a local Large Language Model (`gemma3:1b` via Ollama) to interpret resume content accurately and map it to a structured JSON schema.

## Features

- **Document Parsing**: Extracts text directly from uploaded PDFs and DOCX files.
- **LLM Information Extraction**: Uses the `gemma3:1b` local model to accurately extract candidate details like Name, Email, Experience, Education, Skills, etc.
- **FastAPI Backend**: Provides `POST /api/upload` and `GET /api/resume/{document_id}` endpoints.
- **Interactive UI**: A Streamlit application offering a simple interface to upload files and view the parsed results.
- **Resilient Data Structures**: Uses `pydantic` models to ensure the LLM output conforms exactly to the required REST API response schema.

## Tech Stack
- **Backend Frameowrk**: FastAPI
- **Frontend App**: Streamlit
- **Document Processing**: `pymupdf` (PDF), `python-docx` (DOCX)
- **Data Validation**: Pydantic
- **LLM Engine**: Ollama (Running locally)
- **Logging**: Loguru

## 1. Prerequisites

Before running the application, make sure you have:
1. **Python 3.9+** installed
2. [Ollama](https://ollama.ai/) installed and running locally
3. The `gemma3:1b` model pulled locally:
   ```bash
   ollama run gemma3:1b
   ```
   *Note: Ollama usually runs on port 11434 (`http://localhost:11434`)*

## 2. Setup Instructions

1. **Clone/Navigate to the directory**:
   ```bash
   cd resume-parser
   ```
2. **Create a virtual environment (Optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Copy `.env.example` to `.env` if you need to override the default Ollama Host or Model. (The defaults look for `http://localhost:11434` and `gemma3:1b`).

## 3. Running the Application

This stack involves two separate processes: The Backend (FastAPI) and the Frontend (Streamlit).

### Terminal 1: Start the Backend API
Run the FastAPI Uvicorn server:
```bash
uvicorn app.main:app --reload --port 8000
```
- The API will be available at `http://localhost:8000`
- API documentation (Swagger) is auto-generated at `http://localhost:8000/docs`

### Terminal 2: Start the Frontend UI
In a new terminal, run Streamlit:
```bash
streamlit run ui/streamlit_app.py
```
- The Streamlit interface should open in your browser automatically (usually at `http://localhost:8501`).

## 4. Usage

1. Open the Streamlit web interface showing the **GenAI Resume Parser**.
2. Drag and drop a PDF or DOCX resume into the file uploader.
3. Click **Extract Information**.
4. The backend will process the document text and pass it to Ollama. After a few seconds, the extracted Contact Info, Skills, Education, and Work Experience will populate on the screen.
5. The extracted data is saved in `./data/uploads/` on the server and mapped to a unique `document_id`.

## 5. Technical Explanation (Project Architecture)

The system is structured symmetrically to separate concerns and ensure maintainable code.

- **`app/main.py`**: Points of entry for the API. It defines the paths `/api/upload` (for triggering extraction) and `/api/resume/{document_id}` (for fetching existing extractions).
- **`app/models.py`**: Core schema definitions using `pydantic`. The LLM's response is validated against these models to ensure it conforms.
- **`app/services/parser.py`**: Pure utility library leveraging `pymupdf` and `python-docx` to turn binary blobs into UTF-8 text strings.
- **`app/services/llm_service.py`**: Wraps the connection to Ollama. It accepts raw text, formulates an extraction prompt carrying the JSON schema map, and parses the returned JSON string into Python objects.
- **`app/utils/logger.py`**: Custom structured `loguru` implementation that intercepts standard python logs (and uvicorn logs) for a consistent terminal output.

### How the LLM Extract works:
We pass the document text to `gemma3:1b` with a highly specified prompt. Along with the instructions, we inject `ResumeData.model_json_schema()`. This ensures the foundation model has the exact structure, types, and nested definitions (like `ContactInfo`, `Experience`) it needs to formulate its output cleanly. We also force `format="json"` on the Ollama client call so that the model strictly generates valid JSON rather than mixing it with conversational dialogue.
