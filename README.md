# Message Intelligence Engine

This project is a conversational Q&A system that uses a Retrieval-Augmented Generation (RAG) pipeline to answer questions about a dataset of user messages. It is built using Python, FastAPI, and several modern AI/ML libraries.

## Features

-   **Conversational Q&A:** Allows users to ask questions about the data in a natural way.
-   **Time Intelligence:** The system can reason about relative dates and times (e.g., "next Monday").
-   **RAG Pipeline:** Implements a "Filter-then-Search" strategy for retrieving relevant information before generating an answer.
-   **Automated Data Sync:** A background service continuously ingests new data from an external API.
-   **Multi-LLM Support:** A flexible dispatcher allows for using different LLM providers (e.g., OpenAI, Google Gemini).
-   **Configurable:** Key parameters for the RAG pipeline and chat history are configurable for easier tuning.

## Architecture & Design Notes

The system's architecture is centered around a "Who -> Filter -> Search -> Answer" pipeline. Several design decisions were made to ensure modularity and data integrity.

-   **Database Strategy (SQLite + ChromaDB):**
    -   **Approach:** The system uses SQLite as the permanent "source of truth" for raw message data and ChromaDB as a disposable "search index" for vector embeddings.
    -   **Reasoning:** This separation allows the vector index to be rebuilt at any time (e.g., when updating the embedding model) without risking the source data, ensuring high data integrity and maintainability.

-   **Entity Resolution (Fuzzy Search + LLM):**
    -   **Approach:** A fast fuzzy search (`rapidfuzz`) generates potential candidates for a person's name, and a targeted LLM call then selects the correct entity from that list.
    -   **Reasoning:** While a local NER model would be faster, the LLM-based approach is more powerful for this use case. It allows the system to leverage chat history to resolve pronouns ("his trip") and handle more complex ambiguity.

-   **Retrieval Strategy (Filter-then-Search):**
    -   **Approach:** The system first identifies the entity ("Who") and then performs a filtered vector search on only that entity's messages.
    -   **Reasoning:** This strategy is vastly more efficient and accurate than searching the entire dataset. It prevents "context bleed" from other users and ensures the retrieved documents are highly relevant to the user's query.

## Data Insights

A comprehensive exploratory data analysis (EDA) was performed on the source dataset to understand its structure, content, and limitations.

**The full, detailed report can be found here: [Data Analysis Report](./DATA_ANALYSIS_REPORT.md)**

**Summary of Key Findings:**

-   **API Instability:** The source API is unstable and frequently returns `4xx` errors. The data ingestion service was built with a robust retry mechanism to handle this.
-   **Synthetic Data:** The dataset is synthetic. All 10 users are behavioral clones with near-identical message counts, message length variance, and transactional behavior (~38%).
-   **Data Type:** The data consists of short "Queries" (~12 words avg.), not natural "Chat".
-   **Data Integrity:** The data itself is clean, with no duplicate message IDs and a consistent one-to-one mapping between `user_name` and `user_id`.

---

## API Usage

The primary endpoint for interacting with the Message Intelligence Engine is `/ask`.

### `/ask` Endpoint

-   **Method:** `POST`
-   **URL:** `http://127.0.0.1:11111/ask` (or your configured host/port)
-   **Request Body:**
    ```json
    {
        "question": "Your natural language question here."
    }
    ```
-   **Example Request (using `curl`):**
    ```bash
    curl -X POST "http://127.0.0.1:11111/ask" \
         -H "Content-Type: application/json" \
         -d '{"question": "When is Layla planning her trip to London?"}'
    ```

---

## Project Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/my-chat-intelligence-project.git
    ```
2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file** in the project root and add your API keys:
    ```
    OPENAI_API_KEY="your_openai_key"
    GOOGLE_API_KEY="your_google_key"
    ```
4.  **Run the application:**
    ```bash
    uvicorn message_api.main_entry:app --port 11111 --reload
    ```
    The API will be available at `http://127.0.0.1:11111`.
