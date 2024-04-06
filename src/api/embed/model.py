from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Modality(Enum):
    # VIDEO = "video"
    # IMAGE = "image"
    # AUDIO = "audio"
    TEXT = "text"


class Models(str, Enum):
    MINILM = "sentence-transformers/all-MiniLM-L6-v2"
    NOMIC = "nomic-ai/nomic-embed-text-v1"
    JINA = "jinaai/jina-embeddings-v2-base-en"
    # NOMIC_2 = "nomic-ai/nomic-embed-text-v1.5"
    GOOGLE_BERT = "google-bert/bert-base-multilingual-uncased"


class ConfigsRequest(BaseModel):
    modality: Optional[Modality] = Field(
        default="text", description="The modality of the input data."
    )
    model: Optional[Models] = Field(
        default=Models.MINILM, description="The model to be used for processing."
    )


class ConfigsResponse(BaseModel):
    dimensions: int = Field(..., description="The dimensions of the processed data.")
    elapsed_time: float = Field(..., description="The time taken to process the data.")
    token_size: int = Field(
        ..., description="The size of the tokens in the processed data."
    )


class EmbeddingRequest(BaseModel):
    input: str = Field(..., description="The input data to be processed.")
    modality: Optional[Modality] = Field(
        default="text", description="The modality of the input data."
    )
    model: Optional[str] = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="The model to be used for processing.",
    )


class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(
        ..., description="The embedding of the processed data."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The time taken to process the data."
    )
