import hashlib
from pathlib import Path

from langchain_chroma import Chroma

from app.retrieval.embeddings import get_embedding_model


CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "research_documents"


def get_vector_store():

    embeddings = get_embedding_model()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

    return vector_store


def generate_document_id(file_path: str) -> str:

    path = Path(file_path)

    file_hash = hashlib.sha256()

    with open(path, "rb") as file:

        for chunk in iter(lambda: file.read(8192), b""):
            file_hash.update(chunk)

    return file_hash.hexdigest()


def document_exists(
    vector_store: Chroma,
    document_id: str
) -> bool:

    result = vector_store.get(
        where={
            "document_id": document_id
        },
        limit=1
    )

    return len(result["ids"]) > 0


def add_documents(
    documents,
    document_id: str
):

    vector_store = get_vector_store()

    if document_exists(
        vector_store,
        document_id
    ):

        print(
            f"Document already exists: {document_id}"
        )

        return vector_store

    for document in documents:

        document.metadata["document_id"] = document_id

    vector_store.add_documents(documents)

    print(
        f"Added document: {document_id}"
    )

    return vector_store