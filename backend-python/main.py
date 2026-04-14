import json
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the agent logic
from agent import agent
# Import admin logic
from src.utils import add_new_entry, update, delete, create_connection

load_dotenv()

app = FastAPI(title="Dictionary AI Service")


class ChatQuery(BaseModel):
    query: str


class AcronymEntry(BaseModel):
    acronym: str
    definition: str
    description: str


@app.post("/chat")
async def chat(query: ChatQuery):
    try:
        # Invoke the LangGraph agent
        result = agent.invoke({"messages": [("user", query.query)]})
        # The result typically contains the message history, we want the last one
        if "messages" in result and len(result["messages"]) > 0:
            return {"response": result["messages"][-1].content}
        return {"response": "I'm not sure about that one."}
    except Exception as e:
        print(f"Error calling agent: {e}")
        raise HTTPException(status_code=500, detail="The agent encountered an error.")


@app.post("/admin/add")
async def add_entry(entry: AcronymEntry):
    try:
        # Use the utility function to persist the new acronym
        add_new_entry(entry.acronym, entry.definition, entry.description)
        print(f"Successfully added new acronym: {entry.acronym}")
        return {"message": f"Successfully added {entry.acronym}"}
    except Exception as e:
        print(f"Error adding acronym: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/admin/update")
async def update_entry(entry: AcronymEntry):
    try:
        update(entry.acronym, entry.definition, entry.description)
        return {"message": f"Successfully updated {entry.acronym}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/delete/{acronym}")
async def delete_entry(acronym: str):
    try:
        delete(acronym)
        return {"message": f"Successfully deleted {acronym}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/all-acronyms")
async def get_all_acroyms():
    try:
        with create_connection() as connection:
            cursor = connection.cursor()
            query = """
                    SELECT acronym, definition
                    from acronyms
                    """
            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description]
            all_acronyms = cursor.fetchall()
            data = [dict(zip(columns, acronym)) for acronym in all_acronyms]
            return sorted(data, key=lambda x: x['acronym'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/suggestions")
async def get_suggestions():
    review_list = os.getenv("REVIEW_LIST")
    if not os.path.exists(review_list):
        return []
    try:
        with open(review_list, "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/suggestions/{index}")
async def delete_suggestion(index: int):
    import json
    review_list = os.getenv("REVIEW_LIST")
    if not os.path.exists(review_list):
        return {"message": "No suggestions to delete"}
    try:
        with open(review_list, "r") as file:
            data = json.load(file)
        if index < 0 or index >= len(data):
            raise HTTPException(status_code=404, detail="Suggestion not found")
        data.pop(index)
        with open(review_list, "w") as file:
            json.dump(data, file, indent=4)
        return {"message": "Suggestion removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
