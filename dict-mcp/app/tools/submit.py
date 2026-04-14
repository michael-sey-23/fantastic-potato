from ..http_client import AuthenticatedClient
from ..models import Submission


async def submit(http_client: AuthenticatedClient, submission: Submission) -> str:
    """
    Submit a new acronym to the dictionary.

    This tool adds a new acronym definition to the system. Requires admin authentication.

    Args:
        http_client: The authenticated HTTP client instance
        submission: A Submission object containing:
            - acronym: The acronym to add (e.g., "API")
            - definition: The definition of the acronym (e.g., "Application Programming Interface")
            - description: Optional longer description or context for the acronym

    Returns:
        Success message if the acronym was added, or error message if it failed
    """
    try:
        await http_client.post("api/acronyms/add", json_data={"acronym": submission.acronym, "definition": submission.definition, "description": submission.description})
        return f"'{submission.acronym}' added"
    except Exception as e:
        return f"Failed to add '{submission.acronym}' : {str(e)}"