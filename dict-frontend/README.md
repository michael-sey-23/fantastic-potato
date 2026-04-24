# 📖 AI-Powered Company Acronym Dictionary

---
## Component Deep-Dive

### Angular Frontend (`dict-frontend`)

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
