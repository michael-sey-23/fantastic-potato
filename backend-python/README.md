# 📖 AI-Powered Company Acronym Dictionary

---
## Environment Setup

### Python AI Service — `backend-python/.env`

Copy the example file and fill in the values:

```bash
cp backend-python/.env.example backend-python/.env
```

Open `backend-python/.env` and set:

```env
# Required — your OpenAI API key for the chat model and embeddings
OPENAI_API_KEY=sk-...your-key-here...

# Paths to local data files (defaults are fine for Docker)
ACRONYM_JSON_PATH=assets/words.json
ACRONYM_DB_PATH=assets/acronyms.db
REVIEW_LIST=assets/review.json

# Optional — LangSmith tracing for debugging the AI agent
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=Dictionary
```
---

## Component Deep-Dive

### Python AI Service (`backend-python`)

**Technology:** FastAPI, LangGraph, LangChain, OpenAI (`gpt-5-mini`, `text-embedding-3-small`), ChromaDB, SQLite,
RapidFuzz.

**Architecture — the LangGraph agent:**

The agent in `agent/__init__.py` follows a simple loop:

```
User message → Model (with tools bound) → If tool call → ToolNode → back to Model → … → Final response
```

The model is `gpt-5-mini` bound with three tools:

1. **`retrieve_from_sql_db`** (in `src/tools.py`)
    - Tries an **exact** case-insensitive match in `acronyms.db` first.
    - If not found, runs **fuzzy matching** (RapidFuzz `extractOne`) against all known acronyms, returning a result only
      if the score is ≥ 80.
    - Returns a `source` field (`"exact_match"` or `"fuzzy_match"`) which the agent's system prompt uses to calibrate
      its confidence level.

2. **`retrieve_from_vector_store`** (in `src/tools.py`)
    - Runs a cosine similarity search against ChromaDB using OpenAI embeddings.
    - Returns the single best match and a `source` of `"similarity_search"`.

3. **`user_suggestion`** (in `src/tools.py`)
    - Appends an entry to `assets/review.json` for admin review.
    - Only stores the acronym name and whether it's a new entry or an update — the admin supplies the definition.

**System prompt highlights** (`agent/__init__.py`):

- Never reveal implementation details (databases, fuzzy matching, etc.) to the user.
- Only report results that were actually returned by tools — never fabricate definitions.
- Use the `source` field to set confidence: exact matches are stated with full confidence; similarity results are
  presented as "closest match found."
- If the matched acronym's letters don't logically correspond to the query, do not report it as a match.

**Data storage:**

| Store    | File                 | Purpose                                                                                     |
|----------|----------------------|---------------------------------------------------------------------------------------------|
| SQLite   | `assets/acronyms.db` | Primary acronym store; auto-created by `json_to_db()` from `words.json` if it doesn't exist |
| ChromaDB | `assets/chroma/`     | Vector embeddings for semantic search; synced from SQLite via `sync_vector_store()`         |
| JSON     | `assets/review.json` | Pending user suggestions awaiting admin review                                              |

**Endpoints** (called by the Java backend, not directly by users):

| Endpoint                     | Method | Description                               |
|------------------------------|--------|-------------------------------------------|
| `/chat`                      | POST   | Main agent query endpoint                 |
| `/admin/add`                 | POST   | Add a new acronym to SQLite + ChromaDB    |
| `/admin/update`              | PUT    | Update an existing acronym in both stores |
| `/admin/delete/{acronym}`    | DELETE | Remove from both stores                   |
| `/admin/all-acronyms`        | GET    | List all acronyms sorted alphabetically   |
| `/admin/suggestions`         | GET    | List pending review suggestions           |
| `/admin/suggestions/{index}` | DELETE | Remove a suggestion by array index        |
