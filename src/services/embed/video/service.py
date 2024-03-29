from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import cv2
import numpy as np


class CLIPEmbedder:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def get_image_embedding(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_embedding = self.model.get_image_features(**inputs)
        return (
            image_embedding.cpu()
        )  # Move the embedding back to CPU for further processing or storage

    def get_text_embedding(self, text_query):
        inputs = self.processor(
            text=text_query, return_tensors="pt", padding=True, truncation=True
        ).to(self.device)
        with torch.no_grad():
            text_embedding = self.model.get_text_features(**inputs)
        return text_embedding.cpu()  # Move the embedding back to CPU

    def get_video_embedding(self, video_path, fps=1):
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        embeddings = []

        frame_indices = [
            int(video_fps / fps * i) for i in range(int(frame_count / video_fps * fps))
        ]
        current_frame_index = 0
        success, frame = cap.read()

        while success and current_frame_index < len(frame_indices):
            if current_frame_index == frame_indices[current_frame_index]:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = Image.fromarray(frame)

                frame_embedding = self.get_image_embedding(frame_image)
                embeddings.append(frame_embedding)

                if current_frame_index + 1 < len(frame_indices):
                    cap.set(
                        cv2.CAP_PROP_POS_FRAMES, frame_indices[current_frame_index + 1]
                    )
            current_frame_index += 1
            success, frame = cap.read()

        cap.release()

        if embeddings:
            embeddings = torch.stack(embeddings).to(self.device)
            mean_embedding = torch.mean(embeddings, dim=0)
        else:
            mean_embedding = torch.empty(0).to(self.device)

        return mean_embedding.cpu()  # Move the mean embedding back to CPU


# Example usage remains the same
