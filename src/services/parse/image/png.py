from io import BytesIO
from typing import Union, Dict, List
import torch
from PIL import Image
import requests
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from _exceptions import InternalServerError


class ImageOCRParser:
    def __init__(self):
        # Check for GPU availability
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize model and processor, moving model to the appropriate device
        self.model = VisionEncoderDecoderModel.from_pretrained(
            "microsoft/trocr-base-handwritten"
        ).to(self.device)
        self.processor = TrOCRProcessor.from_pretrained(
            "microsoft/trocr-base-handwritten"
        )

    def parse(self, file_stream: BytesIO, params: Dict) -> Union[List[Dict], str]:
        try:
            # Load image from the file stream
            image = Image.open(file_stream).convert("RGB")

            # Process the image
            pixel_values = self.processor(image, return_tensors="pt").pixel_values

            # Use the model to generate the IDs of the tokens in the transcription
            generated_ids = self.model.generate(pixel_values)

            # Use the processor to convert the token IDs into text
            generated_text = self.processor.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]

            # Return the generated text
            return generated_text
        except Exception as e:
            raise InternalServerError(
                error=f"Failed to parse image. Please try again. If the issue persists, contact support. Exception: {e}"
            )
