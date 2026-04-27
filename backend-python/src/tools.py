import json
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from rapidfuzz import process

from .utils import get_vector_store, create_connection

load_dotenv()

# Resolve paths relative to the project root (backend-python/),
# regardless of which directory this module is imported from.
_src_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_dir)

review_list = os.path.join(_project_root, os.getenv("REVIEW_LIST", "assets/review.json"))


@tool
def retrieve_from_vector_store(user_input: str):
    """
    This tool is responsible for retrieving data from the vector database.
    """
    vectorstore = get_vector_store()
    results = vectorstore.similarity_search_with_score(user_input, k=1)

    if not results:
        return None

    doc, score = results[0]

    # Return the best match regardless of score. The SQL DB will act as fallback
    # if this isn't good enough.
    return {
        "source": "similarity_search",
        "content": doc.page_content
    }


@tool
def retrieve_from_sql_db(user_input: str):
    """
    This tool is responsible for retrieving data from the relational database.
    """
    with create_connection() as connection:
        cursor = connection.cursor()

        # Exact acronym lookups are the safest result, so we always try that before
        # moving to fuzzy matching.
        cursor.execute("""
                       SELECT definition, description
                       FROM acronyms
                       WHERE acronym = ? COLLATE NOCASE
                       """, (user_input,))
        answer = cursor.fetchone()

        if answer:
            res = {
                "source": "exact_match",
                "content": f"{user_input}: {answer[0]}. {answer[1]}"
            }
            return res

        # If there is no exact hit, compare the query against the known acronym list.
        cursor.execute("""SELECT acronym
                          FROM acronyms""")
        acronyms = [row[0] for row in cursor.fetchall()]
        match = process.extractOne(user_input, acronyms)

        if match is None or match[1] < 80:
            return None

        matched_acronym = match[0]
        cursor.execute("""
                       SELECT definition, description
                       FROM acronyms
                       WHERE acronym = ? COLLATE NOCASE
                       """, (matched_acronym,))
        answer = cursor.fetchone()

        if not answer:
            return None

        # result from fuzzy search in SQLite db
        res = {
            "source": "fuzzy_match",
            "content": f"{matched_acronym}: {answer[0]}. {answer[1]}"
        }
        return res


@tool
def user_suggestion(acronym: str, definition: str, description: str, is_new_entry: bool):
    """
    Suggest an addition or update to the database.
    The stored suggestion format is intentionally minimal: only the acronym and a boolean
    flag 'is_new_entry' are persisted. Definition/description are gathered by admins during review.

    Args:
        acronym: The acronym being suggested
        definition: (ignored) kept for compatibility with tool interface
        description: (ignored) kept for compatibility with tool interface
        is_new_entry: True for new acronyms, False for updates
    """
    if not os.path.exists(review_list):
        with open(review_list, 'w') as file:
            json.dump([], file)

    # Suggestions stay outside the main database until an admin reviews them.
    with open(review_list, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    data.append(
        {
            "acronym": acronym,
            "is_new_entry": is_new_entry
        }
    )

    with open(review_list, "w") as file:
        json.dump(data, file, indent=4)

    return "Your entry has been submitted for review by an admin."


tools = [retrieve_from_sql_db, retrieve_from_vector_store, user_suggestion]
