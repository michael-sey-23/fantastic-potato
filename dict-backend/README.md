# 📖 AI-Powered Company Acronym Dictionary

---
## Environment Setup

### Java Backend — `dict-backend/.env`

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
---

## Component Deep-Dive

### Java Backend (`dict-backend`)

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
