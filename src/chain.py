from langchain_core.runnables import RunnablePassthrough

from src.retriever import get_retriever
from src.prompts import get_prompt
from src.llm import get_llm


retriever = get_retriever()
prompt = get_prompt()
llm = get_llm()


def format_docs(docs):
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)