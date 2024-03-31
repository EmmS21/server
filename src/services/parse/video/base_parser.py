import cv2
import torch
from transformers import DetrForObjectDetection, DetrFeatureExtractor, pipeline
from typing import List, Dict, Union
import numpy as np
from io import BytesIO
import tempfile


class VideoParser:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def parse(self, file_stream: BytesIO, params: Dict) -> Union[List[Dict], str]:
        interval = params.get("interval", 5)  # Default interval length of 5 seconds

        # Initialize models based on provided params
        self.object_detector = DetrForObjectDetection.from_pretrained(
            "facebook/detr-resnet-50"
        ).to(self.device)
        self.feature_extractor = DetrFeatureExtractor.from_pretrained(
            "facebook/detr-resnet-50"
        )

        self.keyword_extractor = pipeline(
            "feature-extraction",
            model="distilbert-base-uncased",
            device=0 if torch.cuda.is_available() else -1,
        )

        # Process video
        video_path = self._save_temp_video(file_stream)
        chunks_results = []
        for frames in self._chunk_video(video_path, interval):
            object_detections = self._detect_objects(frames)
            # Placeholder for extracting and processing text to extract keywords
            example_text = "This is a sample text."
            keywords = self._extract_keywords(example_text)
            chunks_results.append(
                {
                    "object_detections": object_detections,
                    "keywords": keywords,
                }
            )

        return chunks_results

    def _save_temp_video(self, file_stream: BytesIO) -> str:
        # Create a temporary file with a suffix '.mp4' to indicate the file type
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            tmp_video.write(file_stream.read())
            # Return the name of the temporary file
            return tmp_video.name

    def _chunk_video(self, video_path: str, interval: int) -> List[np.ndarray]:
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frames = []
        chunk_size = fps * interval

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            if len(frames) == chunk_size:
                yield np.stack(frames)
                frames = []

        if frames:
            yield np.stack(frames)
        cap.release()

    def _detect_objects(self, frames: np.ndarray) -> List[Dict]:
        inputs = self.feature_extractor(frames, return_tensors="pt").to(self.device)
        outputs = self.object_detector(**inputs)
        results = [
            {
                "score": output["scores"].detach().cpu().numpy(),
                "label": output["labels"].detach().cpu().numpy(),
            }
            for output in outputs
        ]
        return results

    def _extract_keywords(self, text: str) -> List[str]:
        # Placeholder method for extracting keywords, adapt based on your keyword extraction logic
        keywords = [word for word in text.split() if len(word) > 4]
        return keywords


# Usage
# parser = VideoParser()
# with open('path/to/video.mp4', 'rb') as video_file:
#     file_stream = BytesIO(video_file.read())
# params = {'interval': 5, 'object_detection_model': 'facebook/detr-resnet-50', 'keyword_model': 'distilbert-base-uncased'}
# results = parser.parse(file_stream, params)
# print(results)
