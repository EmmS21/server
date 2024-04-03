from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

# fmt: off
class Models(str, Enum):
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_4_turbo_preview = "gpt-4-turbo-preview"

class Model(BaseModel):
    provider: str = Field(..., description="The provider of the model.")
    model: Models = Field(..., description="The model to be used.")

class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender.")
    content: str = Field(..., description="The content of the message.")

class Settings(BaseModel):
    system_prompt: Optional[str] = Field(None, description="The system prompt.")
    temperature: Optional[float] = Field(None, description="The temperature for the model.")
    max_tokens: Optional[int] = Field(None, description="The maximum number of tokens for the model.")
    stop: Optional[List[str]] = Field(None, description="The stop tokens for the model.")
    top_p: Optional[float] = Field(None, description="The top_p value for the model.")
    frequency_penalty: Optional[float] = Field(None, description="The frequency penalty for the model.")
    presence_penalty: Optional[float] = Field(None, description="The presence penalty for the model.")

    class Config:
        json_schema_extra = {
            "example": {
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 150,
                "stop": ["\n"],
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }
        }

class GenerationRequest(BaseModel):
    model: Model = Field(..., description="The model to be used.")
    response_format: Optional[Dict] = Field(None, description="The format of the response.")
    context: Optional[str] = Field(None, description="The context for the generation.")
    messages: List[Message] = Field(..., description="The messages for the generation.")
    settings: Optional[Settings] = Field(None, description="The settings for the generation.")

class Metadata(BaseModel):
    elapsed_time: Optional[float] = Field(..., description="The elapsed time for the generation.")
    total_tokens: Optional[int] = Field(..., description="The total number of tokens in the generation.")
    generation_id: Optional[str] = Field(..., description="The ID of the generation.")
    model: Optional[Model] = Field(..., description="The model used for the generation.")
    created_at: Optional[datetime] = Field(..., description="The time the generation was created.")

class GenerationResponse(BaseModel):
    success: bool = Field(..., description="Whether the generation was successful.")
    status: int = Field(..., description="The status code of the generation.")
    error: Optional[dict] = Field(None, description="Any errors that occurred during the generation.")
    response: dict = Field(..., description="The response from the generation.")
    metadata: Optional[Metadata] = Field(..., description="Metadata about the generation.")
