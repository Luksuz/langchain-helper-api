
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_chat_model(model_name: str, temperature: float = 0.0) -> ChatOpenAI:
    """Factory to create a ChatOpenAI client.

    Relies on `OPENAI_API_KEY` env var unless `api_key` is explicit.
    """
    return ChatOpenAI(model=model_name, temperature=temperature)

