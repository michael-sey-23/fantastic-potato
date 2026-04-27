# 📖 AI-Powered Company Acronym Dictionary

---
## Environment Setup

### MCP Server

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
## Component Deep-Dive

### MCP Server (`dict-mcp`)

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