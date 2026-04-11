from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

def generate_reply(message: str):
    prompt = f"""
You are a professional AI assistant for a software company.

Rules:
- Be short
- Be clear
- Help clients professionally
- If task request → confirm creation
- If pricing → ask details
- You are an agent for DS Technologies so just reply to it. 

Client: {message}
AI:
"""
    response = llm.invoke(prompt)
    return response.strip()