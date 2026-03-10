# CON AI - WhatsApp AI Assistant Prototype

This is a prototype for an AI-powered student assistant using FastAPI and Ollama.

## Prerequisites

1.  **Python 3.10+**
2.  **OpenRouter API Key**: You need an API key from [OpenRouter](https://openrouter.ai).

## Installation

1.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Mac/Linux
    ```

2.  Install dependencies:
    ```bash
    pip install fastapi uvicorn requests jinja2 pydantic python-dotenv
    ```

3.  **Setup Environment**:
    Create a `.env` file in the root directory:
    ```env
    OPENROUTER_API_KEY=sk-or-v1-...
    ```

## Running the Application

1.  Start the backend server:
    ```bash
    uvicorn app:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

2.  **Access the Frontend**:
    Open your browser and navigate to:
    [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Debugging

You can run the debug pipeline script to test the backend logic without the browser:

```bash
python debug_pipeline.py
```
