from io import BytesIO
from typing import Union, Dict, List
import torch
from pydub import AudioSegment
import numpy as np
from transformers import Speech2TextProcessor, Speech2TextForConditionalGeneration
from datetime import timedelta
import uuid
from _exceptions import InternalServerError


class MP3Parser:
    def __init__(self):
        # Check for GPU availability
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize model and processor, moving model to the appropriate device
        self.model = Speech2TextForConditionalGeneration.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        ).to(self.device)
        self.processor = Speech2TextProcessor.from_pretrained(
            "facebook/s2t-small-librispeech-asr"
        )

    def parse(self, file_stream: BytesIO, params: Dict) -> Union[List[Dict], str]:
        try:
            audio = AudioSegment.from_mp3(file_stream)
            interval_length_ms = (
                params["interval_range"] * 1000
            )  # Convert seconds to milliseconds
            chunks_dict = []
            for i in range(0, len(audio), interval_length_ms):
                segment = audio[i : i + interval_length_ms]
                text = self.transcribe_audio(segment)
                chunk_dict = {
                    "text": text,
                    "element_id": str(uuid.uuid4()),
                    "metadata": {
                        "timestamp_start": str(timedelta(milliseconds=i)),
                        "timestamp_end": str(
                            timedelta(milliseconds=i + interval_length_ms)
                        ),
                        "languages": ["eng"],
                        "segment_number": 1,
                    },
                }
                chunks_dict.append(chunk_dict)
            return chunks_dict
        except Exception as e:
            raise InternalServerError(
                error=f"Failed to parse MP3. Please try again. If the issue persists, contact support. Exception: {e}"
            )

    def transcribe_audio(self, audio_segment: AudioSegment) -> List[Dict]:
        samples = np.array(audio_segment.get_array_of_samples())
        if audio_segment.channels == 2:
            samples = np.mean(samples.reshape((-1, 2)), axis=1)
        sample_rate = audio_segment.frame_rate

        inputs = self.processor(
            samples, sampling_rate=sample_rate, return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs["input_features"], attention_mask=inputs["attention_mask"]
            )

        transcription_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        return transcription_text
