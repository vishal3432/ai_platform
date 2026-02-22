"""
services/ai_service.py
This module handles all AI/LLM logic.
Keeping it separate from views.
"""
from django.conf import settings


def get_summary(content: str) -> str:
    """
    Summarize the given text using OpenAI GPT.
    Falls back to a simple mock if no API key is set (useful for local dev).

    Parameters:
        content (str): The text to summarize.

    Returns:
        str: The generated summary.
    """
    api_key = settings.OPENAI_API_KEY

    # ── Mock mode (no API key set) ─────────────────────────────────────────
    if not api_key:
        word_count = len(content.split())
        return f"[MOCK SUMMARY] Your text has {word_count} words. Add OPENAI_API_KEY to .env for real summaries."

    # ── Real OpenAI call ───────────────────────────────────────────────────
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Summarize the following text concisely."},
                {"role": "user", "content": content},
            ],
            max_tokens=300,   # Keep responses short
            temperature=0.5,  # Lower = more factual, higher = more creative
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error generating summary: {str(e)}"
