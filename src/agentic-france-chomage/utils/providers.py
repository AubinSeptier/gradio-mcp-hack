"""Utilities for creating API clients for different providers."""

from __future__ import annotations

import os

from openai import OpenAI


def nebius_client() -> OpenAI:
    """Create a Nebius OpenAI-compatible client.

    Returns:
        OpenAI: Configured Nebius client.

    Raises:
        EnvironmentError: If the NEBIUS_API_KEY environment variable is not set.
    """
    api_key = os.getenv("NEBIUS_API_KEY", None)
    if api_key is None:
        raise EnvironmentError("Missing NEBIUS_API_KEY for Nebius client.")
    return OpenAI(base_url="https://api.tokenfactory.nebius.com/v1", api_key=api_key)
