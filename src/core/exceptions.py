"""Custom exceptions for AI Influencer system."""


class AIInfluencerError(Exception):
    """Base exception for AI Influencer system."""
    pass


class ContentGenerationError(AIInfluencerError):
    """Error in content generation process."""
    pass


class PlatformIntegrationError(AIInfluencerError):
    """Error in social media platform integration."""
    pass


class PersonaConsistencyError(AIInfluencerError):
    """Error in maintaining persona consistency."""
    pass


class MediaProcessingError(AIInfluencerError):
    """Error in media processing operations."""
    pass


class DatabaseError(AIInfluencerError):
    """Error in database operations."""
    pass


class APIError(AIInfluencerError):
    """Error in external API calls."""
    pass
