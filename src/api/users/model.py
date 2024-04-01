from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from utilities.helpers import generate_api_key, current_time, generate_uuid
from typing import List, Optional, Union
from utilities.encryption import SecretCipher
from enum import Enum

# {
#   "users": [
#     {
#       "user_id": "123456",
#       "name": "John Doe",
#       "email": "john.doe@example.com",
#       "api_keys": [
#         {
#           "key_id": "api_key_1",
#           "key": "ABCDEFG1234567",
#           "created_at": "2024-03-29T12:34:56Z",
#           "permissions": ["read", "write"]
#         },
#         {
#           "key_id": "api_key_2",
#           "key": "HIJKLMN7654321",
#           "created_at": "2024-03-30T12:34:56Z",
#           "permissions": ["read"]
#         }
#       ],
#       "index_ids": ["index_1", "index_2", "index_3"]
#     }
#   ]
# }


class ConnectionEngine(str, Enum):
    mongodb = "mongodb"
    postgresql = "postgresql"


class Connection(BaseModel):
    engine: ConnectionEngine
    host: str
    port: Optional[int] = None
    database: str
    username: str
    password: str
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
    connections: Optional[List[Connection]] = None


class UserRequest(BaseModel):
    email: EmailStr
    metadata: dict = Field(default_factory=lambda: {})
