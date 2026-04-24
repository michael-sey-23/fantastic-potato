# 📖 AI-Powered Company Acronym Dictionary

A full-stack web application that lets employees look up, manage, and suggest company acronyms through a conversational
AI chat interface. The system combines a Java Spring Boot API, a Python AI service powered by LangGraph and OpenAI, and
an Angular frontend — all orchestrated via Docker Compose.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture & How the Components Fit Together](#2-architecture--how-the-components-fit-together)
3. [Prerequisites](#3-prerequisites)
4. [Environment Setup](#4-environment-setup)
5. [Running the Application](#5-running-the-application)
6. [Accessing the Application](#6-accessing-the-application)
7. [Feature Walkthrough](#7-feature-walkthrough)
8. [Component Deep-Dive](#8-component-deep-dive)
    - [Angular Frontend (`dict-frontend`)](#81-angular-frontend-dict-frontend)
    - [Java Backend (`dict-backend`)](#82-java-backend-dict-backend)
    - [Python AI Service (`backend-python`)](#83-python-ai-service-backend-python)
    - [MCP Server (`dict-mcp`)](#84-mcp-server-dict-mcp)
9. [Database Details](#9-database-details)
10. [Authentication & Security](#10-authentication--security)
11. [Admin Functions](#11-admin-functions)
12. [API Reference](#12-api-reference)
13. [Development Without Docker](#13-development-without-docker)
14. [Project Structure](#14-project-structure)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. System Overview

This application solves a common workplace problem: employees encounter acronyms they don't recognise and have no
central place to look them up. The solution is a chat-based interface where a user types a question like *"What does BRD
mean?"* and an AI agent looks it up from a managed dictionary, responding in natural language.

**Key capabilities:**

- **Chat interface** — ask about acronyms conversationally; the AI understands context.
- **Smart search** — uses exact matching, fuzzy matching, and semantic (vector) search so queries still work even with
  typos or partial information.
- **User suggestions** — any logged-in user can suggest a new acronym or correction; it goes into a review queue.
- **Admin dashboard** — admins can add, edit, delete, and approve suggested acronyms.
- **Search history** — every search is saved per user so they can revisit past lookups.
- **MCP Server** — a Model Context Protocol server allowing external AI tools (e.g., Claude Desktop) to query and add
  acronyms programmatically.

---

## 2. Architecture & How the Components Fit Together

```
┌──────────────────────────────────────────────────────────────────┐
│                          User's Browser                          │
│                   Angular SPA  (port 80)                         │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP (REST + JWT)
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│               Java Spring Boot Backend  (port 8080)              │
│  - Authentication (JWT + OAuth2 Google/GitHub)                   │
│  - User & search history stored in PostgreSQL                    │
│  - Forwards chat queries → Python AI Service                     │
│  - Admin CRUD endpoints → Python AI Service                      │
└───────────┬──────────────────────────────────┬───────────────────┘
            │ HTTP                             │ JDBC
            ▼                                 ▼
┌───────────────────────┐          ┌──────────────────────┐
│  Python AI Service    │          │  PostgreSQL Database │
│  (FastAPI, port 8000) │          │  (port 5432)         │
│                       │          │  - users_table       │
│  LangGraph Agent      │          │  - search_history    │
│  ┌─────────────────┐  │          └──────────────────────┘
│  │  OpenAI GPT     │  │
│  │  gpt-5-mini     │  │
│  └────────┬────────┘  │
│           │tool calls │
│  ┌────────▼────────┐  │
│  │  Tools          │  │
│  │ • SQL lookup    │──┼──► SQLite DB (acronyms.db)
│  │ • Vector search │──┼──► ChromaDB  (chroma/)
│  │ • User suggest  │──┼──► review.json
│  └─────────────────┘  │
└───────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              MCP Server  (port 8002, stdio transport)            │
│  Allows external AI tools to search/add acronyms via the         │
│  Java backend API using an authenticated HTTP client.            │
└──────────────────────────────────────────────────────────────────┘
```

### Request flow for a chat search

1. The user types a question in the Angular chat UI.
2. Angular sends `GET /api/acronyms/search?query=<text>` to the Java backend (with a JWT in the `Authorization` header).
3. Java forwards the query as a POST to the Python service's `/chat` endpoint.
4. The Python LangGraph agent decides which tool(s) to call:
    - **`retrieve_from_sql_db`** — tries an exact acronym match first; falls back to fuzzy matching (RapidFuzz,
      threshold 80%).
    - **`retrieve_from_vector_store`** — semantic similarity search via ChromaDB + OpenAI embeddings.
5. The agent formulates a natural-language response and returns it.
6. Java saves the query + response to the PostgreSQL `search_history` table and returns the result to Angular.
7. Angular displays the response in the chat bubble.

---

## 3. Prerequisites

Before you begin, make sure the following are installed on your machine:

| Tool                                                              | Minimum Version | Purpose                                                              |
|-------------------------------------------------------------------|-----------------|----------------------------------------------------------------------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24+             | Runs all services in containers                                      |
| [Docker Compose](https://docs.docker.com/compose/)                | 2.20+           | Orchestrates the multi-container setup (bundled with Docker Desktop) |
| An **OpenAI API key**                                             | —               | Powers the AI chat agent and embeddings                              |

> **No Java, Python, or Node.js installation is required** on your host machine — Docker handles everything.

---

## 4. Environment Setup

Each service needs a `.env` file with its secrets. These files are intentionally excluded from version control (see
`.gitignore`). You must create them manually.

### 4.1 Python AI Service — `backend-python/.env`

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

### 4.2 Java Backend — `dict-backend/.env`

Copy the example file:

```bash
cp dict-backend/.env.example dict-backend/.env
```

Open `dict-backend/.env` and set:

```env
# PostgreSQL connection (matches the db service in docker-compose.yml)
SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/dictionary_db
SPRING_DATASOURCE_USERNAME=user
SPRING_DATASOURCE_PASSWORD=password

# JWT secret — CHANGE THIS to a long random string in any non-local environment
JWT_SECRET=replace_with_a_long_random_secret_string_here

# URL of the Python AI service (use the Docker service name)
PYTHON_SERVICE_URL=http://python-ai:8000

# Optional — OAuth2 social login (leave blank to disable)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

> **Important:** The `JWT_SECRET` must be at least 32 characters long. You can generate one with:
> ```bash
> openssl rand -base64 48
> ```

### 4.3 What about the MCP Server?

The MCP server (`dict-mcp`) gets its configuration directly from `docker-compose.yml` via the `environment:` block — no
separate `.env` file is needed:

```yaml
environment:
  JAVA_BASE_URL: http://java-backend:8080
  ADMIN_USERNAME: admin
  ADMIN_PASSWORD: password123
```

If you change the default admin password, update these values to match.

---

## 5. Running the Application

Once both `.env` files are in place, start everything with a single command from the **project root** (the folder
containing `docker-compose.yml`):

```bash
docker compose up --build
```

The `--build` flag tells Docker to (re)build all service images. On the **first run** this takes several minutes as it
downloads base images and installs dependencies. Subsequent starts are much faster.

**What happens during startup:**

1. **PostgreSQL** starts first and initialises the `dictionary_db` database.
2. **Python AI Service** starts and loads the AI model configuration.
3. **Java Backend** connects to PostgreSQL, runs Hibernate schema migrations (`ddl-auto: update`), and creates a default
   `admin` user with password `password123` if one doesn't already exist.
4. **Angular Frontend** is served by Nginx on port 80.
5. **MCP Server** waits for the Java backend to pass its health check before starting.

### Stopping the application

```bash
docker compose down
```

To also delete the PostgreSQL data volume (a complete reset):

```bash
docker compose down -v
```

---

## 6. Accessing the Application

| Service               | URL                   | Notes                                    |
|-----------------------|-----------------------|------------------------------------------|
| **Web Application**   | http://localhost      | Main Angular UI                          |
| **Java API**          | http://localhost:8080 | REST API; use Postman or browser         |
| **Python AI Service** | http://localhost:8000 | Internal; not meant for direct use       |
| **Adminer (DB GUI)**  | http://localhost:8081 | Inspect the PostgreSQL database          |
| **MCP Server**        | localhost:8002        | stdio transport for AI tool integrations |

### Default login credentials

| Username | Password      | Role                |
|----------|---------------|---------------------|
| `admin`  | `password123` | Admin — full access |

You can register additional standard user accounts through the Sign Up form in the application. New accounts always
receive the `USER` role; admin accounts must be created directly in the database or by modifying `DataInitializer.java`.

---

## 7. Feature Walkthrough

### Logging In

Navigate to http://localhost. You'll see the login page. Enter the credentials above or register a new account.
Optionally, if you configured Google/GitHub OAuth2 credentials, you can use the social login buttons.

### Chat (Search)

After logging in you land on the **Chat** page. Type any acronym or description in the input box and press Enter or
click the send button. The AI will respond with a definition. Examples:

- `"What is NPS?"`
- `"What does BRD stand for?"`
- `"What term describes the measure of how satisfied a customer is with a product or service?"`

Below the chat window is a collapsible panel showing all acronyms in the dictionary — click the toggle arrow to expand
it.

### History

The **History** page (clock icon in the sidebar) shows all your past searches in a master/detail layout. Click any entry
on the left to see the full question and AI response on the right. You can filter entries using the search box.

### Admin Dashboard

Only visible to users with the `ADMIN` role. Accessible via the shield icon in the sidebar. From here you can:

- **Add a new acronym** — fill in the acronym, definition, and description, then click Add.
- **Review user suggestions** — any time a chat user suggests an addition or update, it appears here. Click **Review**to
  pre-fill the add form with the acronym, add the definition/description, and approve it. Click **Reject** to discard.
- **Edit/delete existing acronyms** — click any acronym card in the "All Acronyms" list to open the edit popup.

---

## 8. Component Deep-Dive

### 8.1 Angular Frontend (`dict-frontend`)

**Technology:** Angular 21, TypeScript, standalone components, Angular Signals.

**Key files:**

| File                          | Purpose                                                                                                                       |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `src/app/app.routes.ts`       | Defines all routes; `isLoggedInGuard` protects authenticated routes, `authGuard` protects admin routes                        |
| `src/app/auth.service.ts`     | Manages JWT tokens in `localStorage`; exposes reactive `isLoggedIn`, `isAdmin`, and `isTokenExpired` computed signals         |
| `src/app/auth-interceptor.ts` | HTTP interceptor that attaches the `Bearer` token to every outgoing request and handles 401 responses by logging the user out |
| `src/app/chat-service.ts`     | Maintains the in-memory chat history (as a signal); sends queries to the Java API and appends responses to the history        |
| `src/app/search/`             | The main chat UI component                                                                                                    |
| `src/app/history/`            | Search history master/detail view                                                                                             |
| `src/app/admin/`              | Admin dashboard with add/edit/delete/review forms                                                                             |
| `src/app/login/`              | Login and registration form                                                                                                   |
| `src/app/app.env.ts`          | Central place for `API_URL` and `BASE_URL` constants — **change these if you deploy to a non-localhost host**                 |

**Build & deployment:** The `Dockerfile` uses a two-stage build — Node.js compiles the Angular app into static files,
which Nginx then serves. The `default.conf` Nginx config includes `try_files $uri /index.html` so Angular's client-side
routing works correctly on page refresh.

---

### 8.2 Java Backend (`dict-backend`)

**Technology:** Spring Boot 4, Spring Security, Spring Data JPA, WebFlux (for reactive HTTP calls to Python), JJWT,
PostgreSQL.

**Key files:**

| File                     | Purpose                                                                                                                         |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `SecurityConfig.java`    | Configures CORS, disables CSRF (stateless API), sets up JWT filter, OAuth2 login, and endpoint permissions                      |
| `JwtRequestFilter.java`  | Extracts and validates JWT from the `Authorization` header on every request                                                     |
| `JwtUtils.java`          | Generates and validates JWT tokens; tokens contain the username and role, expire after 10 hours                                 |
| `AuthController.java`    | `POST /api/auth/login` and `POST /api/auth/register` endpoints                                                                  |
| `AcronymController.java` | All acronym endpoints — search, history, add, update, delete, suggestions                                                       |
| `ChatService.java`       | Spring WebClient bean that makes HTTP calls to the Python AI service; base URL is configurable via `PYTHON_SERVICE_URL` env var |
| `DataInitializer.java`   | Seeds the default `admin` account on startup if it doesn't exist                                                                |
| `SearchHistory.java`     | JPA entity saved to `search_history` table every time a search is made                                                          |
| `application.yaml`       | All Spring configuration; credentials are read from environment variables                                                       |

**How it communicates with Python:** `ChatService` uses Spring's reactive `WebClient`. For a chat search, it POSTs
`{"query": "<user input>"}` to `http://python-ai:8000/chat`. For admin operations (add/update/delete), it calls the
corresponding `/admin/*` endpoints on the Python service.

---

### 8.3 Python AI Service (`backend-python`)

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

---

### 8.4 MCP Server (`dict-mcp`)

**Technology:** Python, FastMCP (from the `mcp` library), httpx.

The MCP server exposes the dictionary to external AI assistants (like Claude Desktop) as a set of callable tools. It
authenticates with the Java backend as the `admin` user and holds a JWT for the lifetime of the process.

**Tools exposed:**

| Tool          | Description                                                                                           |
|---------------|-------------------------------------------------------------------------------------------------------|
| `search_tool` | Takes a `Query` object (with a `query` string) and returns the definition from the Java API           |
| `submit_tool` | Takes a `Submission` object (acronym, definition, description) and adds it directly to the dictionary |

**How to connect to Claude Desktop:** Configure your `claude_desktop_config.json` to point to the MCP server. Since the
Docker container runs with `sleep infinity`, you interact with it via `docker exec`. Alternatively, run the MCP server
directly in stdio mode:

```bash
cd dict-mcp
pip install -e .
python -m app.main
```

---

## 9. Database Details

### PostgreSQL (managed by Java backend)

Tables are created automatically by Hibernate on startup (`ddl-auto: update`).

| Table            | Key Columns                                               | Description                                        |
|------------------|-----------------------------------------------------------|----------------------------------------------------|
| `users_table`    | `id`, `username`, `password`, `role`, `email`, `provider` | Stores user accounts; passwords are BCrypt-hashed  |
| `search_history` | `id`, `query`, `response`, `username`, `search_time`      | One row per search; scoped to the user who made it |

### SQLite (managed by Python service)

Stored at `backend-python/assets/acronyms.db`. The `acronyms` table has three columns: `acronym` (primary key),
`definition`, `description`.

You can pre-populate it from a JSON file by calling `json_to_db()` from `src/utils.py`. The JSON format expected is:

```json
[
  {
    "acronym": "",
    "definition": "",
    "description": ""
  }
]
```

### ChromaDB

Stored at `backend-python/assets/chroma/`. It is kept in sync with SQLite: every add/update/delete operation in the
Python service calls both SQLite and ChromaDB. If they ever get out of sync, call `sync_vector_store()` from
`src/utils.py` to rebuild ChromaDB from SQLite.

---

## 10. Authentication & Security

### JWT Authentication (primary method)

1. User POSTs credentials to `POST /api/auth/login`.
2. Spring validates credentials against the `users_table`.
3. A JWT is returned containing the username and role (`ROLE_USER` or `ROLE_ADMIN`), signed with the `JWT_SECRET`, valid
   for 10 hours.
4. The Angular app stores this in `localStorage` as `auth_token`.
5. The `authInterceptor` attaches it as `Authorization: Bearer <token>` on every subsequent request.
6. The `JwtRequestFilter` on the Java side validates the token and sets the Spring Security context.
7. The Angular app also checks token expiry every 60 seconds via `setInterval` in `App` component, and the interceptor
   checks it proactively before each request.

### OAuth2 Social Login (optional)

If `GOOGLE_CLIENT_ID` / `GITHUB_CLIENT_ID` are configured, users can log in with their Google or GitHub account. On
success, Spring creates or retrieves the user record, generates a JWT, and redirects to
`http://localhost/oauth2/redirect?token=<jwt>`. The Angular `OAuth2Redirect` component captures the token and stores it
identically to the standard login flow.

### Role-based access

| Role         | Capabilities                                                    |
|--------------|-----------------------------------------------------------------|
| `ROLE_USER`  | Search, view own history, suggest acronyms via chat             |
| `ROLE_ADMIN` | All of the above + add/edit/delete acronyms, review suggestions |

---

## 11. Admin Functions

### Via the Web UI

Log in as `admin`, then click the **Admin** link (shield icon) in the sidebar.

### Via the Command Line (Python)

The `backend-python/admin.py` script provides a terminal-based admin interface for when the web UI isn't available. Run
it inside the Python container:

```bash
docker exec -it dict-python python admin.py
```

Options:

1. Add a new acronym
2. Update an existing entry
3. Delete an entry
4. Review user suggestions (walks through `review.json` interactively)
5. Exit

### Via Postman

Import `Dictionary API.postman_collection.json` into Postman. The collection includes:

- A **Login** request that automatically saves the JWT to a collection variable.
- Pre-configured requests for all acronym endpoints.

Set the `base_url` collection variable to `http://localhost:8080` (the default).

---

## 12. API Reference

All endpoints are prefixed with `http://localhost:8080`. Authenticated endpoints require`Authorization: Bearer <token>`.

### Authentication

| Method | Endpoint             | Auth | Body                              | Description                |
|--------|----------------------|------|-----------------------------------|----------------------------|
| POST   | `/api/auth/login`    | None | `{"username":"…","password":"…"}` | Returns JWT token          |
| POST   | `/api/auth/register` | None | `{"username":"…","password":"…"}` | Creates a new USER account |

### Acronyms

| Method | Endpoint                            | Auth  | Description                                          |
|--------|-------------------------------------|-------|------------------------------------------------------|
| GET    | `/api/acronyms/search?query=<text>` | User  | AI-powered search; saves to history                  |
| GET    | `/api/acronyms/history`             | User  | Returns the current user's search history            |
| GET    | `/api/acronyms/all-acronyms`        | User  | Lists all acronyms alphabetically                    |
| POST   | `/api/acronyms/add`                 | Admin | `{"acronym":"…","definition":"…","description":"…"}` |
| PUT    | `/api/acronyms/update`              | Admin | `{"acronym":"…","definition":"…","description":"…"}` |
| DELETE | `/api/acronyms/delete/{acronym}`    | Admin | Deletes by acronym name                              |
| GET    | `/api/acronyms/suggestions`         | Admin | Lists pending review suggestions                     |
| DELETE | `/api/acronyms/suggestions/{index}` | Admin | Removes a suggestion by its array index              |

---

## 13. Development Without Docker

If you want to run services individually for development:

### Python AI Service

```bash
cd backend-python
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in OPENAI_API_KEY
python main.py
# Runs on http://localhost:8000
```

### Java Backend

Requires Java 17 and a running PostgreSQL instance. Update `application.yaml` or set environment variables for
`SPRING_DATASOURCE_URL`, etc.

```bash
cd dict-backend
./mvnw spring-boot:run
# Runs on http://localhost:8080
```

### Angular Frontend

Requires Node.js 20+.

```bash
cd dict-frontend
npm install
ng serve
# Runs on http://localhost:4200
```

> **Note:** When running locally, the Angular app's `API_URL` in `src/app/app.env.ts` defaults to
`http://localhost:8080/api/` — this matches the Java backend's default port, so no changes are needed for local
> development.

---

## 14. Project Structure

```
project-root/
│
├── docker-compose.yml          # Orchestrates all services
├── requirements.in             # Python top-level deps (for uv/pip-compile)
├── requirements.txt            # Pinned Python deps
├── Dictionary API.postman_collection.json  # Postman collection for testing
│
├── backend-python/             # Python AI Service
│   ├── Dockerfile
│   ├── .env.example            # → copy to .env and fill in secrets
│   ├── main.py                 # FastAPI app entry point
│   ├── admin.py                # CLI admin tool
│   ├── requirements.txt
│   ├── langgraph.json          # LangGraph Cloud config (optional)
│   ├── agent/
│   │   └── __init__.py         # LangGraph agent definition
│   ├── src/
│   │   ├── tools.py            # LangChain tools (SQL, vector, suggestion)
│   │   └── utils.py            # DB helpers, sync functions
│   └── assets/
│       ├── words.json          # Optional seed data
│       ├── acronyms.db         # SQLite database (auto-created)
│       ├── review.json         # Pending suggestions
│       └── chroma/             # ChromaDB vector store (auto-created)
│
├── dict-backend/               # Java Spring Boot Backend
│   ├── Dockerfile
│   ├── .env.example            # → copy to .env and fill in secrets
│   ├── docker-compose.yml      # For running only the DB locally
│   ├── pom.xml
│   └── src/main/java/com/dictionary/dict_backend/
│       ├── config/             # DataInitializer, WebClientConfig
│       ├── controller/         # AcronymController, AuthController
│       ├── model/              # User, Role, SearchHistory
│       ├── repository/         # JPA repositories
│       ├── security/           # JWT, OAuth2, filters, Spring Security config
│       └── service/            # ChatService (WebClient to Python)
│
├── dict-frontend/              # Angular Frontend
│   ├── Dockerfile
│   ├── default.conf            # Nginx config with SPA routing
│   ├── src/app/
│   │   ├── app.env.ts          # API URL constants
│   │   ├── app.routes.ts       # Route definitions + guards
│   │   ├── auth.service.ts     # JWT management
│   │   ├── auth-interceptor.ts # HTTP interceptor
│   │   ├── chat-service.ts     # Chat state management
│   │   ├── models.ts           # TypeScript interfaces
│   │   ├── search/             # Chat page
│   │   ├── history/            # History page
│   │   ├── admin/              # Admin dashboard
│   │   ├── login/              # Login/register page
│   │   └── oauth2-redirect/    # OAuth2 callback handler
│   └── public/
│       └── acronyms.json       # Static fallback data (not used in production)
│
└── dict-mcp/                   # MCP Server
    ├── Dockerfile
    ├── pyproject.toml
    └── app/
        ├── main.py             # FastMCP server + tool registration
        ├── models.py           # Pydantic models (Query, Submission)
        ├── http_client.py      # Authenticated HTTP client for Java API
        └── tools/
            ├── search.py       # search_tool implementation
            └── submit.py       # submit_tool implementation
```

---

## 15. Troubleshooting

### The app shows "AI service unavailable"

The Java backend cannot reach the Python service. Check:

```bash
docker compose logs python-ai
```

Common causes:

- Missing or invalid `OPENAI_API_KEY` in `backend-python/.env`
- The Python container crashed on startup

### Login fails with "Invalid username or password"

- Confirm you're using `admin` / `password123` (case-sensitive)
- If you deleted the database volume, the admin account is re-created on the next Java startup — wait for the Java
  container to be healthy

### "Permission denied" or Docker errors on startup

On Linux/WSL2, ensure Docker has permissions for the bind-mounted `assets/` directory:

```bash
chmod -R 777 backend-python/assets
```

### ChromaDB is returning wrong results

The vector store may be out of sync with SQLite. Resync by running:

```bash
docker exec -it dict-python python -c "from src.utils import sync_vector_store; sync_vector_store()"
```

### The Angular app doesn't update after code changes

If running via Docker, you must rebuild the frontend image:

```bash
docker compose up --build angular-frontend
```

### Adminer (database GUI) access

Navigate to http://localhost:8081 and log in with:

- **System:** PostgreSQL
- **Server:** `db`
- **Username:** `user`
- **Password:** `password`
- **Database:** `dictionary_db`

### Viewing logs for a specific service

```bash
docker compose logs -f java-backend    # Java backend
docker compose logs -f python-ai       # Python AI service
docker compose logs -f angular-frontend # Nginx/Angular
docker compose logs -f db              # PostgreSQL
```

---

## Notes for New Maintainers

- **Adding new acronyms in bulk:** Prepare a JSON file matching the format in `assets/words.json` and call`json_to_db()`
  followed by `sync_vector_store()`.
- **Changing the AI model:** Edit `agent/__init__.py` — replace `"gpt-5-mini"` with your preferred OpenAI model name.
- **Deploying to production:** Update `API_URL` in `dict-frontend/src/app/app.env.ts` to your server's domain, set a
  strong `JWT_SECRET`, and consider replacing SQLite with a production-grade database for the acronym store.
- **The `REVIEW_LIST` path:** `assets/review.json` is bind-mounted into the Docker container via the `volumes:` entry in
  `docker-compose.yml`. This means suggestions persist across container restarts.
