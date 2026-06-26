from langchain_core.prompts import PromptTemplate


def get_prompt():

    return PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an organizational knowledge assistant.

Rules:
1. Answer ONLY from the provided context.
2. Do not use external knowledge.
3. If answer is missing, say:
   "The information is not available in the book."
4. Keep answers factual.

Context:
{context}

Question:
{question}

Answer:
"""
    )