from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Union

from utilities.helpers import generate_api_key, current_time, generate_uuid
from utilities.encryption import SecretCipher


# Enums
class PricingTier(str, Enum):
    free = "free"
    deluxe = "deluxe"
    premium = "premium"
    startup = "startup"
    enterprise = "enterprise"


class ConnectionEngine(str, Enum):
    mongodb = "mongodb"
    postgresql = "postgresql"


# Base Schemas
class Permissions(BaseModel):
    rate_limit: str = Field(default="10/minute")  # requests per minute


class UsagePricing(BaseModel):
    credits: int = Field(default=1000)
    pricing_tier: PricingTier = Field(default=PricingTier.free)


class ApiKeyScope(BaseModel):
    user_ids: Optional[List[str]] = None


class ApiKey(BaseModel):
    name: str
    key: str = Field(default_factory=lambda: "sk-" + generate_api_key())
    scope: ApiKeyScope = Field(default_factory=ApiKeyScope)
    indexes: List[str] = Field(default_factory=list)


class Connection(BaseModel):
    engine: ConnectionEngine
    host: str
    port: Optional[int] = None
    database: str
    username: str
    password: bytes
    extra_params: Optional[dict] = None
    # connection_id: str = Field(
    #     default_factory=lambda: "conn-" + generate_uuid(length=6, dashes=False)
    # )

    @property
    def password(self):
        cipher = SecretCipher()
        return cipher.decrypt_string(self.password)

    @password.setter
    def password(self, new_value):
        cipher = SecretCipher()
        # Check if the password is already encrypted
        if not cipher.is_encrypted(new_value):
            self._password = cipher.encrypt_string(new_value)
        else:
            self._password = new_value

    # Validate the port based on the type of database
    @validator("port", always=True)
    def set_default_port(cls, v, values):
        if "engine" in values:
            if values["engine"] == ConnectionEngine.mongodb and v is None:
                return 27017

        return v

    # Example of how you might validate extra parameters for a specific database type, if necessary
    @validator("extra_params", always=True)
    def validate_extra_params(cls, v, values):
        if "engine" in values:
            if values["engine"] == ConnectionEngine.mongodb:
                # MongoDB specific validation can go here
                pass
        return v


# User and Organization Models
class User(BaseModel):
    email: EmailStr
    creation_date: datetime = Field(default_factory=current_time)
    metadata: dict = Field(default_factory=dict)
    scope: str = Field(default="organization")


class OrganizationBase(BaseModel):
    org_id: str = Field(default_factory=lambda: "org-" + generate_api_key())
    indexes: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    creation_date: datetime = Field(default_factory=current_time)
    api_keys: List[ApiKey] = Field(default_factory=list)
    users: List[User] = Field(default_factory=list)
    permissions: Permissions
    usage: UsagePricing
    connections: List[Connection] = Field(default_factory=list)


# Trusted Response Models
class TrustedUserResponse(BaseModel):
    email: EmailStr
    creation_date: datetime
    metadata: dict
    scope: str


class TrustedOrgResponse(BaseModel):
    org_id: str
    indexes: List[str]
    metadata: dict
    creation_date: datetime
    users: List[TrustedUserResponse]
    permissions: Permissions
    usage: UsagePricing
    # api_keys: List[ApiKey] = Field(default_factory=list)
    # connections: List[Connection] = Field(default_factory=list)


# Request Models
class CreateOrgRequest(BaseModel):
    email: EmailStr
    org_metadata: Optional[dict] = {}
    user_metadata: Optional[dict] = {}


class OrganizationUpdateRequest(BaseModel):
    metadata: Optional[dict] = None
    api_keys: Optional[List[ApiKey]] = None
    users: Optional[List[User]] = None
    permissions: Optional[Permissions] = None
    # usage: Optional[UsagePricing] = None
    connections: Optional[List[Connection]] = None
