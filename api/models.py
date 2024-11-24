from pydantic import BaseModel

class FunctionQuery(BaseModel):
    carousel: str
    input: str


