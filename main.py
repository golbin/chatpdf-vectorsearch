import os
from PyPDF2 import PdfReader
from fastapi import FastAPI
from datastore import Datastore
from models import Document, Query, File

db = Datastore("chatpdf")

app = FastAPI()


@app.post("/load")
async def load(file: File):
    filename = os.path.basename(file.path)
    fulltext = ""

    with open(file.path, "rb") as f:
        pdf = PdfReader(f)

        for page in pdf.pages:
            text = page.extract_text()
            chunks = [text[i:i+1000] for i in range(0, len(text), 900)]
            pageNum = pdf.get_page_number(page)
            fulltext += text

            for i, chunk in enumerate(chunks):
                doc = Document(
                    id=f"{filename}-p{pageNum}-{i}",
                    text=chunk,
                    metadata={"filename": filename, "page": pageNum}
                )

                print("Upserting: ", doc.id)
                db.upsert(doc)

    return {
        "filename": filename,
        "total_pages": len(pdf.pages),
        "text": fulltext
    }


@app.post("/query")
async def query(query: Query) -> list[Document]:
    result = db.query(query.filename, query.query, query.top_k)

    print(query.filename, query.query)
    # print(result)

    return result
