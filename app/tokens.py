"""Token estimation when the provider does not report usage.

Rule of thumb for English text with GPT-style tokenizers: about 4 characters per token.
It is an estimate only; always prefer the usage numbers the provider returns.
"""


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))