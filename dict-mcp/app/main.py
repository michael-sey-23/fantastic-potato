import os
import sys
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .http_client import AuthenticatedClient
from .models import Submission, Query
from .tools.search import search
from .tools.submit import submit

load_dotenv()

# Ensure UTF-8 encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Initialize FastMCP server
mcp = FastMCP("dictionary", host="0.0.0.0", port=8002)

# The MCP tools share one authenticated backend client instead of logging in per call.
http_client: Optional[AuthenticatedClient] = None


async def get_http_client() -> AuthenticatedClient:
    """Get or create the HTTP client with authentication."""
    global http_client

    if http_client is None:
        base_url = os.getenv("JAVA_BASE_URL")
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        # MCP calls go through the same secured Java API used by the frontend.
        http_client = AuthenticatedClient(base_url, admin_username, admin_password)

        try:
            await http_client.login()
            print("Login success", file=sys.stderr)
        except Exception as e:
            print(f"Login failed: {str(e)}", file=sys.stderr)
            raise

    return http_client


@mcp.tool()
async def search_tool(query: Query) -> dict:
    """
    Search for an acronym definition in the dictionary.

    Args:
        query: A Query object containing the query to search for

    Returns:
        Dictionary containing the definition or error message
    """
    client = await get_http_client()
    return await search(client, query)


@mcp.tool()
async def submit_tool(submission: Submission) -> dict:
    """
    Submit a new acronym to the dictionary.

    Args:
        submission: A Submission object containing:
            - acronym: The acronym to add
            - definition: The definition of the acronym
            - description: Optional longer description

    Returns:
        Success or error message
    """
    client = await get_http_client()
    return await submit(client, submission)


if __name__ == "__main__":
    import asyncio

    # Failing fast here is easier to diagnose than starting the server with broken credentials.
    asyncio.run(get_http_client())
    mcp.run(transport="stdio")
