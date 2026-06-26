from langchain_community.vectorstores import Chroma

from src.embeddings import get_embeddings


def get_retriever():

    db = Chroma(
        persist_directory="chroma_db",
        embedding_function=get_embeddings()
    )

    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    return retriever