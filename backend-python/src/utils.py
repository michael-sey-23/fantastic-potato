import json
import os
import sqlite3

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Resolve project root (backend-python/) and normalize environment paths (strip surrounding quotes)
_src_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_dir)

def _get_env_path(var_name: str, default: str):
    val = os.getenv(var_name, default)
    if val is None:
        return default
    # Strip surrounding quotes if present and normalize relative paths
    val = val.strip().strip('"').strip("'")
    if not os.path.isabs(val):
        return os.path.join(_project_root, val)
    return val

acronym_json_path = _get_env_path("ACRONYM_JSON_PATH", os.path.join(_project_root, "assets", "words.json"))
persist_directory = os.path.join(_project_root, "assets", "chroma")
sql_db_path = _get_env_path("ACRONYM_DB_PATH", os.path.join(_project_root, "assets", "acronyms.db"))


def get_embeddings():
    return OpenAIEmbeddings(model="text-embedding-3-small")


def get_vector_store():
    return Chroma(
        collection_name="dictionary",
        persist_directory=persist_directory,
        embedding_function=get_embeddings()
    )


def create_connection(db_name=sql_db_path):
    """
    Creates and returns a SQLite database connection.
    Raises a ValueError if the database path is not configured.
    """
    if not db_name:
        raise ValueError("ACRONYM_DB_PATH is not set. Please set ACRONYM_DB_PATH in the environment or .env")
    # Ensure parent directory exists for sqlite file
    db_dir = os.path.dirname(db_name)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(db_name)


def json_to_db(file=acronym_json_path):
    """Add entries from a json file to an sqlite database"""
    insert_query = """
                   INSERT OR IGNORE INTO acronyms (acronym, definition, description)
                   VALUES (?, ?, ?); \
                   """

    with open(file) as f:
        data = json.load(f)

    with create_connection() as connection:
        cursor = connection.cursor()

        for item in data:
            cursor.execute(
                insert_query,
                (
                    item['acronym'],
                    item['definition'],
                    item['description']
                )
            )

        connection.commit()


def sql_to_document():
    """Convert sqlite database entries to Documents"""
    with create_connection() as connection:
        cursor = connection.cursor()

        docs = []
        ids = []

        cursor.execute("SELECT acronym, definition, description FROM acronyms")
        for row in cursor:
            docs.append(Document(
                page_content=f"{row[0]}: {row[1]}. {row[2]}"
            ))
            ids.append(row[0])
    return docs, ids


def sync_vector_store():
    """Sync all acronyms from sql database into the vector store using upsert"""

    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)

    docs, ids = sql_to_document()

    if not docs:
        print("No documents found.")
        return

    vectorstore = get_vector_store()
    vectorstore.add_documents(documents=docs, ids=ids)
    print(f"Synced {len(docs)} documents to ChromaDB.")


def add_new_entry(new_acronym: str, new_definition: str, new_description: str):
    """
    Append a new entry to the sql database and upsert it into the vector store.
    acronym is the acronym to be added, for example AOB.
    definition is the acronym in its full form. AOB's definition would be 'Any Other Business'.
    description is an explanation of the acronym.
    """

    with create_connection() as connection:
        cursor = connection.cursor()
        insert_query = """
                       INSERT OR REPLACE INTO acronyms (acronym, definition, description)
                       VALUES (?, ?, ?);
                       """
        cursor.execute(
            insert_query,
            (
                new_acronym,
                new_definition,
                new_description
            )
        )
        connection.commit()

    doc = Document(
        page_content=f"{new_acronym}: {new_definition}. {new_description}"
    )

    vectorstore = get_vector_store()
    vectorstore.add_documents(documents=[doc], ids=[new_acronym])
    print(f"Added '{new_acronym}' to SQLite database and ChromaDB.")


def update(acronym, new_definition, new_description):
    """
    Update an existing term in the databases
    """
    with create_connection() as connection:
        cursor = connection.cursor()
        update_query = """
                       UPDATE acronyms
                       SET definition  = ?,
                           description = ?
                       WHERE acronym = ?
                       """
        cursor.execute(
            update_query,
            (
                new_definition,
                new_description,
                acronym
            )
        )
        connection.commit()

        doc = Document(
            page_content=f"{acronym}: {new_definition}. {new_description}"
        )
        vectorstore = get_vector_store()
        vectorstore.add_documents(documents=[doc], ids=[acronym])
    print(f"Updated acronym: '{acronym}' in database")


def delete(acronym):
    """
    Delete an entry from the databases
    """
    with create_connection() as connection:
        cursor = connection.cursor()
        delete_query = """
                       DELETE
                       FROM acronyms
                       WHERE acronym = ? \
                       """
        cursor.execute(
            delete_query,
            (acronym,)
        )
        connection.commit()
        vectorstore = get_vector_store()
        vectorstore.delete(ids=[acronym])
    print(f"Deleted '{acronym}' from database")
