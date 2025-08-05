"""Test configuration for pytest."""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_character_config():
    """Sample character configuration for testing."""
    return {
        "name": "TestInfluencer",
        "demographics": {
            "age": "25",
            "gender": "neutral",
            "ethnicity": "mixed",
            "style": "modern"
        },
        "personality": {
            "tone": "friendly",
            "expertise": "technology",
            "interests": ["AI", "tech"]
        },
        "visual_style": {
            "clothing": "casual",
            "settings": "office",
            "accessories": "glasses"
        }
    }


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "text": "This is a test post about AI technology.",
        "hashtags": ["#AI", "#Technology", "#Innovation"],
        "platform": "instagram",
        "media_type": "image"
    }
