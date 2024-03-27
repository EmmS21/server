from io import BytesIO
from typing import Union, Dict, List
from unstructured.partition.xlsx import partition_xlsx
from unstructured.chunking.basic import chunk_elements
from unstructured.cleaners.core import clean

from .base_parser import ParserInterface
from ..model import XLSXParams
from _exceptions import InternalServerError


class XLSXParser(ParserInterface):

    def parse(self, file_stream: BytesIO, params: XLSXParams) -> Union[List[Dict], str]:
        try:
            elements = partition_xlsx(
                file=file_stream, include_header=params.include_header
            )
            chunks = chunk_elements(
                elements=elements,
                max_characters=params.max_characters_per_chunk,
            )
            chunks_dict = [chunk.to_dict() for chunk in chunks]

            if params.clean_text:
                chunks_dict = [
                    {**c, "text": self._clean_chunk_text(c["text"])}
                    for c in chunks_dict
                ]

            if params.should_chunk:
                return chunks_dict
            else:
                combined_text = " ".join([c["text"] for c in chunks_dict])
                return combined_text

        except Exception as e:
            raise InternalServerError(
                error="Failed to parse XLSX. Please try again. If the issue persists, contact support."
            )

    def _clean_chunk_text(self, text: str) -> str:
        return clean(
            text=text,
            extra_whitespace=True,
            dashes=True,
            bullets=True,
            trailing_punctuation=True,
        )
