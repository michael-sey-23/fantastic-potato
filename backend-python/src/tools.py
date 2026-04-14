import json
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from rapidfuzz import process

from src.utils import get_vector_store, create_connection

load_dotenv()

review_list = os.getenv("REVIEW_LIST")


@tool
def retrieve_from_vector_store(user_input: str):
    """
    This tool is responsible for retrieving data from the vector database.
    """

    vectorstore = get_vector_store()
    answer = vectorstore.similarity_search_with_score(user_input, k=1)

    if not answer:
        return "No results found."

    doc, score = answer[0]

    if score > 0.9:
        answer = vectorstore.similarity_search_with_score(user_input, k=3)
        if not answer:
            return "No results found."
        return [doc.page_content for doc, score in answer]

    # result when a description is input to find a term
    res = {
        "source": "similarity_search",
        "content": f"{doc.metadata.get('acronym')} - {doc.metadata.get('definition')}"
    }
    return res


@tool
def retrieve_from_sql_db(user_input: str):
    """
    This tool is responsible for retrieving data from the relational database.
    """
    with create_connection() as connection:
        cursor = connection.cursor()

        # try to find an exact match first
        cursor.execute("""
                       SELECT definition, description
                       FROM acronyms
                       WHERE acronym = ? COLLATE NOCASE
                       """, (user_input,))
        answer = cursor.fetchone()

        if answer:
            res = {
                "source": "exact_match",
                "content": f"{user_input} : {answer[0]}"
            }
            return res

        # fuzzy match fallback
        cursor.execute("""SELECT acronym FROM acronyms""")
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
            "content": f"{matched_acronym} : {answer[0]}"
        }
        return res


@tool
def user_suggestion(acronym: str, new_acronym: bool):
    """
    Suggest an addition or update to the database
    The user's entry is put into a file to be reviewed by an admin to confirm the entry.
    Use this tool when a user suggests a new entry or an updated entry.
    If a user has a new entry to add or update, you should ask them to input the acronym, so that it is clear what data to use.
    new_acronym should be set to True if it is a new acronym
    new_acronym should be set to False if it is an update
    """
    if not os.path.exists(review_list):
        with open(review_list, 'w') as file:
            json.dump([], file)

    with open(review_list, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    data.append(
        {
            "acronym" : acronym,
            "metadata": {
                "new_acronym" : new_acronym
            }
        }
    )

    with open(review_list, "w") as file:
        json.dump(data, file, indent=4)

    return "Your entry has been submitted to be reviewed by an admin"


tools = [retrieve_from_sql_db, retrieve_from_vector_store, user_suggestion]
