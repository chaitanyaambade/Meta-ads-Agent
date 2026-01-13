"""
Custom exceptions for META Marketing Agent System
"""


class MetaAgentError(Exception):
    """Base exception for all agent errors"""
    pass


class APIError(MetaAgentError):
    """API request failed"""
    def __init__(self, message: str, code: int = None, status_code: int = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(MetaAgentError):
    """Invalid input parameters"""
    pass


class CampaignCreationError(MetaAgentError):
    """Campaign creation failed"""
    pass


class AdSetCreationError(MetaAgentError):
    """Ad set creation failed"""
    pass


class AssetError(MetaAgentError):
    """Asset upload/retrieval failed"""
    pass


class AdAgentError(MetaAgentError):
    """Base exception for ad agent"""
    pass


class CreativeError(AdAgentError):
    """Creative creation/retrieval failed"""
    pass


class AdCreationError(AdAgentError):
    """Ad creation failed"""
    pass
