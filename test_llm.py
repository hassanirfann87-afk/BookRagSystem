from src.llm import get_llm

llm = get_llm()

response = llm.invoke("What is Artificial Intelligence?")

print(response)