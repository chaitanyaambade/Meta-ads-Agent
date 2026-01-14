"""
Data models for META Marketing Agent System
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List

from .exceptions import ValidationError


class CampaignObjective(str, Enum):
    """Valid campaign objectives"""
    AWARENESS = "OUTCOME_AWARENESS"
    TRAFFIC = "OUTCOME_TRAFFIC"
    ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    LEADS = "OUTCOME_LEADS"
    APP_PROMOTION = "OUTCOME_APP_PROMOTION"
    SALES = "OUTCOME_SALES"


class CampaignStatus(str, Enum):
    """Campaign status values"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class CampaignParams:
    """Campaign creation parameters - accepts any fields from JSON"""

    def __init__(self, **kwargs):
        """
        Initialize with any campaign parameters

        Args:
            **kwargs: Any campaign parameters (name, objective, budget, etc.)
        """
        # Required fields
        if "name" not in kwargs:
            raise ValueError("Campaign 'name' is required")
        if "objective" not in kwargs:
            raise ValueError("Campaign 'objective' is required")

        # Store all fields
        self.params = kwargs

        # Set defaults if not provided
        if "status" not in self.params:
            self.params["status"] = "PAUSED"
        if "special_ad_categories" not in self.params:
            self.params["special_ad_categories"] = ["NONE"]

        # Validate budget if present
        if "daily_budget" in self.params and self.params["daily_budget"] < 4000:
            raise ValueError("Daily budget must be at least 4000 paisa")
        if "lifetime_budget" in self.params and self.params["lifetime_budget"] < 4000:
            raise ValueError("Lifetime budget must be at least 4000 paisa")

    @property
    def name(self) -> str:
        """Get campaign name"""
        return self.params.get("name")

    @property
    def objective(self) -> str:
        """Get campaign objective"""
        return self.params.get("objective")

    @property
    def status(self) -> str:
        """Get campaign status"""
        return self.params.get("status", "PAUSED")

    def to_api_dict(self) -> Dict:
        """Convert to API request format - pass all fields"""
        return self.params.copy()


class AdSetParams:
    """Flexible Ad set creation parameters - accepts any fields from JSON"""

    def __init__(self, **kwargs):
        # Require minimal identifying fields
        if "name" not in kwargs:
            raise ValidationError("Ad set 'name' is required")

        self.params = kwargs.copy()

        # Defaults
        if "status" not in self.params:
            self.params["status"] = "PAUSED"
        if "billing_event" not in self.params:
            self.params["billing_event"] = "IMPRESSIONS"

        # Validate budgets if present
        if "daily_budget" in self.params and self.params["daily_budget"] is not None:
            try:
                if int(self.params["daily_budget"]) < 4000:
                    raise ValidationError("Ad set 'daily_budget' must be at least 4000 paisa")
            except ValueError:
                raise ValidationError("Ad set 'daily_budget' must be an integer amount in paisa")
        if "lifetime_budget" in self.params and self.params["lifetime_budget"] is not None:
            try:
                if int(self.params["lifetime_budget"]) < 4000:
                    raise ValidationError("Ad set 'lifetime_budget' must be at least 4000 paisa")
            except ValueError:
                raise ValidationError("Ad set 'lifetime_budget' must be an integer amount in paisa")

    @property
    def name(self) -> str:
        return self.params.get("name")

    @property
    def campaign_id(self) -> Optional[str]:
        return self.params.get("campaign_id")

    @campaign_id.setter
    def campaign_id(self, value: str):
        self.params["campaign_id"] = value

    @property
    def optimization_goal(self) -> Optional[str]:
        return self.params.get("optimization_goal")

    @property
    def status(self) -> str:
        return self.params.get("status", "PAUSED")

    def to_api_dict(self) -> Dict:
        """Return a copy of all provided fields to send to the API"""
        return self.params.copy()


@dataclass
class Campaign:
    """Campaign response model"""
    id: str
    name: str
    objective: str
    status: str
    created_time: Optional[str] = None


@dataclass
class AdSet:
    """Ad set response model"""
    id: str
    name: str
    campaign_id: str
    optimization_goal: str
    status: str


@dataclass
class Creative:
    """Creative response model"""
    id: str
    name: str
    data: Dict[str, Any]


@dataclass
class Ad:
    """Ad response model"""
    id: str
    name: str
    data: Dict[str, Any]


class LeadFormQuestionType(str, Enum):
    """Valid lead form question types"""
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    FULL_NAME = "FULL_NAME"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    CITY = "CITY"
    STATE = "STATE"
    COUNTRY = "COUNTRY"
    ZIP = "ZIP"
    STREET_ADDRESS = "STREET_ADDRESS"
    POST_CODE = "POST_CODE"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    DOB = "DOB"
    GENDER = "GENDER"
    MARITAL_STATUS = "MARITAL_STATUS"
    RELATIONSHIP_STATUS = "RELATIONSHIP_STATUS"
    MILITARY_STATUS = "MILITARY_STATUS"
    WORK_EMAIL = "WORK_EMAIL"
    WORK_PHONE_NUMBER = "WORK_PHONE_NUMBER"
    JOB_TITLE = "JOB_TITLE"
    COMPANY_NAME = "COMPANY_NAME"
    CUSTOM = "CUSTOM"


class LeadFormParams:
    """Lead form creation parameters - accepts any fields from JSON"""

    def __init__(self, **kwargs):
        """
        Initialize with lead form parameters

        Args:
            **kwargs: Lead form parameters (name, questions, privacy_policy, etc.)
        """
        # Required fields
        if "name" not in kwargs:
            raise ValidationError("Lead form 'name' is required")
        if "questions" not in kwargs:
            raise ValidationError("Lead form 'questions' is required")
        if "privacy_policy" not in kwargs:
            raise ValidationError("Lead form 'privacy_policy' is required")

        # Validate privacy_policy has url
        privacy_policy = kwargs.get("privacy_policy", {})
        if not isinstance(privacy_policy, dict) or "url" not in privacy_policy:
            raise ValidationError("Lead form 'privacy_policy.url' is required")

        # Store all fields
        self.params = kwargs

        # Set defaults
        if "locale" not in self.params:
            self.params["locale"] = "en_US"

        # Validate questions array
        self._validate_questions(self.params.get("questions", []))

    def _validate_questions(self, questions: list):
        """Validate questions array structure"""
        if not isinstance(questions, list) or len(questions) == 0:
            raise ValidationError("Lead form 'questions' must be a non-empty array")

        for idx, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValidationError(f"Question {idx} must be an object")
            if "type" not in question:
                raise ValidationError(f"Question {idx} missing 'type' field")

    @property
    def name(self) -> str:
        return self.params.get("name")

    @property
    def questions(self) -> list:
        return self.params.get("questions", [])

    @property
    def privacy_policy(self) -> dict:
        return self.params.get("privacy_policy", {})

    @property
    def locale(self) -> str:
        return self.params.get("locale", "en_US")

    def to_api_dict(self) -> Dict:
        """Convert to API request format"""
        return self.params.copy()


@dataclass
class LeadForm:
    """Lead form response model"""
    id: str
    name: str
    status: str
    page_id: str
    locale: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    created_time: Optional[str] = None


@dataclass
class Lead:
    """Lead response model"""
    id: str
    form_id: str
    created_time: str
    field_data: Dict[str, Any]
    ad_id: Optional[str] = None
    ad_name: Optional[str] = None
    adset_id: Optional[str] = None
    campaign_id: Optional[str] = None
