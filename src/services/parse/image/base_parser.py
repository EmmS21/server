from io import BytesIO
from typing import Union, Dict, List
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from _exceptions import InternalServerError


class ImageParser:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.feature_extractor = None
        self.tokenizer = None

    def init_model(self, strategy):
        # Initialize model, processor, and tokenizer based on strategy
        if strategy not in ["ocr", "object", "auto"]:
            raise ValueError(
                "Unsupported strategy. Choose either 'ocr' or 'object' or 'auto'."
            )

        self.model = VisionEncoderDecoderModel.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        ).to(self.device)
        self.feature_extractor = ViTImageProcessor.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "nlpconnect/vit-gpt2-image-captioning"
        )

    def parse(
        self, file_stream: BytesIO, params: Dict = None
    ) -> Union[List[Dict], str]:
        strategy = params.image_settings.get("strategy")
        if not strategy:
            raise ValueError(
                "Strategy not specified in params['image_settings']['strategy']"
            )

        self.init_model(strategy)

        try:
            # Load image from the file stream
            image = Image.open(file_stream).convert("RGB")

            # Process the image
            pixel_values = self.feature_extractor(
                images=[image], return_tensors="pt"
            ).pixel_values.to(self.device)

            # Generation kwargs
            gen_kwargs = {"max_length": 16, "num_beams": 4}

            # Generate captions
            output_ids = self.model.generate(pixel_values, **gen_kwargs)

            # Decode the generated captions
            preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
            return preds
        except Exception as e:
            raise InternalServerError(
                error=f"Failed to parse image. Please try again. If the issue persists, contact support. Exception: {e}"
            )
