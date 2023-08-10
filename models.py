from pydantic import BaseModel


class Metadata(BaseModel):
    filename: str
    page: int


class Document(BaseModel):
    id: str
    text: str
    metadata: Metadata


class File(BaseModel):
    path: str


class Query(BaseModel):
    filename: str
    query: str
    top_k: int
