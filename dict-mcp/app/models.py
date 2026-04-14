from pydantic import BaseModel

# Submission and Query input schema
class Submission(BaseModel):
    acronym: str
    definition: str
    description: str | None = None


class Query(BaseModel):
    query: str
