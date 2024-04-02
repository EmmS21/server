from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from utilities.helpers import generate_api_key, current_time, generate_uuid
from typing import List, Optional, Union
from utilities.encryption import SecretCipher
from enum import Enum


class ConnectionEngine(str, Enum):
    mongodb = "mongodb"
    postgresql = "postgresql"


class Connection(BaseModel):
    engine: ConnectionEngine
    host: str
    port: Optional[int] = None
    database: str
    username: str
    password: bytes
    extra_params: Optional[dict] = None

    # Encrypt password before saving
    @validator("password", pre=True, always=True)
    def encrypt_password(cls, v):
        if isinstance(v, str):
            cipher = SecretCipher()
            return cipher.encrypt_string(v)
        return v  # Assuming it's already encrypted if not a str

    # Method to decrypt password for use, not as a validator
    def get_decrypted_password(self):
        cipher = SecretCipher()
        return cipher.decrypt_string(self.password)


class APIKey(BaseModel):
    key: str = Field(default_factory=lambda: "sk-" + generate_api_key())
    name: str = Field(default_factory=lambda: "default")
    created_at: datetime = Field(default_factory=lambda: current_time())
    # permissions: List[str] = Field(default_factory=lambda: ["read", "write"])


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: generate_uuid(10, False))
    email: EmailStr
    api_keys: List[APIKey] = Field(default_factory=lambda: [APIKey()])
    index_ids: List[str] = Field(default_factory=lambda: ["ix-" + generate_api_key()])
    metadata: dict = Field(default_factory=lambda: {})
    connections: Optional[List[Connection]] = Field([])


class UserRequest(BaseModel):
    email: EmailStr
    metadata: dict = Field(default_factory=lambda: {})


class UpdateUserRequest(BaseModel):
    api_keys: Optional[List[APIKey]] = Field(None)
    metadata: Optional[dict] = Field(None)
    connections: Optional[List[Connection]] = Field(None)

    class Config:
        extra = "forbid"  # forbid extra fields
