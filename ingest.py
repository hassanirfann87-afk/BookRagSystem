from langchain_community.document_loaders import (
    PyPDFDirectoryLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_community.vectorstores import Chroma

from src.embeddings import get_embeddings


loader = PyPDFDirectoryLoader("books")

documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(
    documents
)

db = Chroma.from_documents(
    documents=chunks,
    embedding=get_embeddings(),
    persist_directory="chroma_db"
)


db.persist()

print("Indexing Completed")
print(f"Total Chunks: {len(chunks)}")