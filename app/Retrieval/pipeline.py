from langchain_core.documents import Document

class DocuumentLoader:
    def load(self,source:str):
        """
        Load documents from the given source.
        """
        raise NotImplementedError(
            "Document loading is not implemented yet."
        )