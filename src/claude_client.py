"""
Handles all Anthropic API calls with exponential backoff retry.
"""

import os
import time

import anthropic

MODEL = "claude-opus-4-7"
MAX_TOKENS = 2048
MAX_RETRIES = 4


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def call(system: str, messages: list[dict], max_tokens: int = MAX_TOKENS) -> str:
    client = _client()
    delay = 2
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            return response.content[0].text
        except anthropic.RateLimitError as e:
            last_error = e
            time.sleep(delay)
            delay *= 2
        except anthropic.APIStatusError as e:
            last_error = e
            if e.status_code < 500:
                raise
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f"Claude API failed after {MAX_RETRIES} attempts: {last_error}")


def call_prompt(prompt: dict) -> str:
    return call(
        system=prompt["system"],
        messages=prompt["messages"],
    )
