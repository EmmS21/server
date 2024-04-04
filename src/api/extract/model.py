from pydantic import BaseModel, Field, root_validator
from typing import Optional
from _exceptions import BadRequestError


class PartitionStrategy:
    AUTO = "auto"
    FAST = "fast"
    OCR_ONLY = "ocr_only"
    HI_RES = "hi_res"


class ImageStrategy:
    OCR = "ocr"
    OBJECT = "object"
    AUTO = "auto"


class PDFParams(BaseModel):
    strategy: str = Field(
        default=PartitionStrategy.AUTO,
        description="""The strategy to use for partitioning the PDF. Valid strategies are "hi_res",
        "ocr_only", and "fast". When using the "hi_res" strategy, the function uses
        a layout detection model to identify document elements. When using the
        "ocr_only" strategy, partition_pdf simply extracts the text from the
        document using OCR and processes it. If the "fast" strategy is used, the text
        is extracted directly from the PDF. The default strategy `auto` will determine
        when a page can be extracted using `fast` mode, otherwise it will fall back to `hi_res`.""",
    )
    infer_table_structure: Optional[bool] = Field(
        default=False,
        description="Applicable if strategy='hi_res'. If True, extracts tables with their structure preserved as HTML.",
    )
    hi_res_model_name: Optional[str] = Field(
        default=None,
        description="The layout detection model used when partitioning strategy is set to 'hi_res'.",
    )


class HTMLParams(BaseModel):
    skip_headers_and_footers: Optional[bool] = Field(
        default=False,
        description="If True, ignores any content that is within <header> or <footer> tags",
    )


class CSVParams(BaseModel):
    include_header: Optional[bool] = Field(
        default=False,
        description="Determines whether or not header info is included in text and medatada.text_as_html",
    )


class PPTParams(BaseModel):
    pass


class PPTXParams(BaseModel):
    pass


class XLSXParams(BaseModel):
    include_header: Optional[bool] = Field(
        default=False,
        description="Determines whether or not header info is included in text and medatada.text_as_html",
    )


class TXTParams(BaseModel):
    pass


class AudioParams(BaseModel):
    interval_range: Optional[int] = Field(
        default=5,
        description="The range of time in seconds to split the audio into chunks.",
    )


class ImageParams(BaseModel):
    strategy: str = Field(
        default=ImageStrategy.AUTO,
        description="The strategy to use for parsing the image. Valid strategies are 'ocr', 'object', and 'auto'.",
    )


class VideoParams(BaseModel):
    pass


class ExtractRequest(BaseModel):
    # Common Settings across Parsers
    file_url: Optional[str] = Field(
        default=None,
        description="URL of the file to be parsed. Either 'file_url' or 'contents' must be provided, but not both.",
    )
    contents: Optional[str] = Field(
        default=None,
        description="Either 'file_url' or 'contents' must be provided, but not both.",
    )

    should_chunk: Optional[bool] = Field(
        True, description="Indicates if the text should be divided into chunks."
    )
    clean_text: Optional[bool] = Field(
        True, description="Indicates if the text should be cleaned."
    )
    max_characters_per_chunk: Optional[int] = Field(
        None,
        description="The maximum number of characters per chunk. None means no limit.",
    )

    # Common Settings across Parsers
    extract_tags: Optional[bool] = Field(
        False, description="Indicates if tags should be extracted from the text."
    )
    summarize: Optional[bool] = Field(
        False, description="Indicates if the text should be summarized."
    )

    # Parser Specific Settings for text/unstructured
    pdf_settings: Optional[PDFParams] = PDFParams()
    html_settings: Optional[HTMLParams] = HTMLParams()
    csv_settings: Optional[CSVParams] = CSVParams()
    ppt_settings: Optional[PPTParams] = PPTParams()
    pptx_settings: Optional[PPTXParams] = PPTXParams()
    xlsx_settings: Optional[XLSXParams] = XLSXParams()
    txt_settings: Optional[TXTParams] = TXTParams()

    # Parser Specific Settings for audio
    audio_settings: Optional[AudioParams] = AudioParams()

    # Parser Specific Settings for image
    image_settings: Optional[ImageParams] = ImageParams()

    # Parser Specific Settings for video
    video_settings: Optional[VideoParams] = VideoParams()

    @root_validator(pre=True)
    def check_mutually_exclusive_fields(cls, values):
        file_url, contents = values.get("file_url", None), values.get("contents", None)
        if file_url and contents:
            raise BadRequestError(
                error={
                    "message": "Only one of 'file_url' or 'contents' can be provided."
                }
            )
        if not file_url and not contents:
            raise BadRequestError(
                error={"message": "Either 'file_url' or 'contents' must be provided."}
            )
        return values


class ExtractResponse(BaseModel):
    output: list = Field(..., description="The output of the extraction process.")
    metadata: dict = Field(
        ..., description="Metadata related to the extraction process."
    )
    elapsed_time: Optional[float] = Field(
        default=None, description="The time taken to process the data."
    )
