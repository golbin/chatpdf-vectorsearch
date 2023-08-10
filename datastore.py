import os

import chromadb
from chromadb.utils import embedding_functions

from models import Document


client = chromadb.PersistentClient(path="./chromadb")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],
    model_name="text-embedding-ada-002"
)


class Datastore:
    def __init__(self, collection_name):
        self.collection_name = collection_name

        try:
            self.collection = client.get_collection(
                name=collection_name, embedding_function=openai_ef)
        except ValueError as e:
            self.collection = client.create_collection(
                name=collection_name, embedding_function=openai_ef)

    def upsert(self, doc: Document):
        self.collection.add(
            ids=[doc.id],
            documents=[doc.text],
            metadatas=[doc.metadata.dict()],
        )

        return doc

    def delete(self, id: str):
        self.collection.delete(ids=[id])

    def query(self, filename: str, query: str, top_k: int) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"filename": filename},
        )

        docs = []
        for i in range(len(results["ids"][0])):
            doc = Document(
                id=results["ids"][0][i],
                text=results["documents"][0][i],
                metadata=results["metadatas"][0][i],
                distance=results["distances"][0][i],
            )

            docs.append(doc)

        return docs
