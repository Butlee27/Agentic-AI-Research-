from app.retrieval.retriever import retrieve_documents as search_documents


def retrieve_documents(query: str) -> str:

    documents = search_documents(query)

    if not documents:
        return "No relevant documents were found."

    context_parts = []

    for document in documents:

        context_parts.append(
            document.page_content
        )

    return "\n\n".join(context_parts)