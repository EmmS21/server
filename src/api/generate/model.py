from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


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
    system_prompt: Optional[str] = Field(default=None, description="The system prompt.")
    temperature: Optional[float] = Field(
        default=None, description="The temperature for the model."
    )
    max_tokens: Optional[int] = Field(
        default=None, description="The maximum number of tokens for the model."
    )
    stop: Optional[List[str]] = Field(
        default=None, description="The stop tokens for the model."
    )
    top_p: Optional[float] = Field(
        default=None, description="The top_p value for the model."
    )
    frequency_penalty: Optional[float] = Field(
        default=None, description="The frequency penalty for the model."
    )
    presence_penalty: Optional[float] = Field(
        default=None, description="The presence penalty for the model."
    )

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
    response_format: Optional[Dict] = Field(
        default=None, description="The format of the response."
    )
    context: Optional[str] = Field(
        default=None, description="The context for the generation."
    )
    messages: List[Message] = Field(..., description="The messages for the generation.")
    settings: Optional[Settings] = Field(
        default=None, description="The settings for the generation."
    )


class Metadata(BaseModel):
    total_tokens: Optional[int] = Field(
        ..., description="The total number of tokens in the generation."
    )
    generation_id: Optional[str] = Field(..., description="The ID of the generation.")
    model: Optional[Model] = Field(
        ..., description="The model used for the generation."
    )


class GenerationResponse(BaseModel):
    response: dict = Field(..., description="The response from the generation.")
    metadata: Optional[Metadata] = Field(
        ..., description="Metadata about the generation."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The time taken to process the data."
    )
