"""Shared OpenRouter-compatible LLM client."""
import os
from functools import lru_cache
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_client():
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to the .env file.")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "AI Grant Proposal Generator"
        }
    )

def ask_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2,
            max_tokens: int = 3000) -> str:
    """Send a bounded chat-completion request and return text."""
    model = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    response = get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    text = response.choices[0].message.content
    if not text:
        raise RuntimeError("The model returned an empty response.")
    return text.strip()
