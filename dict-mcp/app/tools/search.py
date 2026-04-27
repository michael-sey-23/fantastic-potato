from ..http_client import AuthenticatedClient
from ..models import Query


async def search(http_client: AuthenticatedClient, query: Query) -> dict:
    """
    Search for an acronym definition.

    This tool looks up an acronym in the dictionary and returns its definition.

    Args:
        http_client: The authenticated HTTP client instance
        query: The acronym to search for (e.g., "API")

    Returns:
        Dictionary with either:
        - "definition": The definition of the acronym if found
        - "error": Error message if the acronym was not found or request failed
    """
    try:
        response = await http_client.get(
            "api/acronyms/search",
            query=query.query
        )

        if response and len(response) > 0:
            # The Java API returns a list payload, so MCP unwraps the first match.
            definition = response[0]["definition"]
            return f"{query.query} = {definition}"
        else:
            return f"No definition found for '{query.query}'"

    except Exception as e:
        return f"Failed to look up '{query.query}': {str(e)}"
