"""
LLM Service - Unified interface for Gemini and Ollama (Llama)
"""

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings


def get_llm() -> BaseChatModel:
    """Get the configured LLM instance based on settings."""
    
    if settings.LLM_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set. Add it to your .env file.")
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
    
    elif settings.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.3,
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")


# RAG prompt template
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer the question using ONLY the information from the context below
- If the context doesn't contain enough information, say so clearly
- Be concise and direct in your response
- Quote relevant parts of the context when appropriate"""),
    ("human", """Context:
{context}

Question: {question}

Answer:""")
])


def create_qa_chain():
    """Create a simple QA chain for answering questions."""
    llm = get_llm()
    return RAG_PROMPT | llm | StrOutputParser()


def format_context(documents: list) -> str:
    """Format retrieved documents into context string."""
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(context_parts)

