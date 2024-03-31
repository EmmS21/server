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

    def preprocess_audio(self, audio: AudioSegment) -> AudioSegment:
        return audio.set_frame_rate(16000)

    def parse(self, file_stream: BytesIO, params: Dict) -> Union[List[Dict], str]:
        try:
            settings = params.audio_settings
            audio = AudioSegment.from_mp3(file_stream)
            audio = self.preprocess_audio(audio)  # Resample audio to 16000 Hz
            interval_length_ms = (
                settings["interval_range"] * 1000
            )  # Convert seconds to milliseconds
            chunks_dict = []
            segment_number = 0
            for i in range(0, len(audio), interval_length_ms):
                # Slice the audio into a segment of length 'interval_length_ms' starting at index 'i'
                segment = audio[i : i + interval_length_ms]
                text = self.transcribe_audio(segment)
                segment_number += 1
                chunk_dict = {
                    "text": text,
                    "element_id": str(uuid.uuid4()),
                    "metadata": {
                        "timestamp_start": str(timedelta(milliseconds=i)),
                        "timestamp_end": str(
                            timedelta(milliseconds=i + interval_length_ms)
                        ),
                        "languages": ["eng"],
                        "segment_number": segment_number,
                    },
                }
                chunks_dict.append(chunk_dict)
            return chunks_dict
        except Exception as e:
            raise InternalServerError(
                error=f"Failed to parse MP3. Please try again. If the issue persists, contact support. Exception: {e}"
            )

    def transcribe_audio(self, audio_segment: AudioSegment) -> List[Dict]:
        # Convert the audio segment into an array of samples
        samples = np.array(audio_segment.get_array_of_samples())

        # If the audio is stereo (2 channels), convert it to mono by taking the mean of the two channels
        if audio_segment.channels == 2:
            samples = np.mean(samples.reshape((-1, 2)), axis=1)

        # Get the sample rate of the audio segment
        sample_rate = audio_segment.frame_rate

        # Use the processor to prepare the samples for the model
        # The processor resamples the audio to the sample rate the model was trained on, and converts the audio samples into the format expected by the model
        inputs = self.processor(
            samples, sampling_rate=sample_rate, return_tensors="pt"
        ).to(self.device)

        # Use the model to generate the IDs of the tokens in the transcription
        # The model takes the processed audio samples and returns the IDs of the tokens in the transcription
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs["input_features"], attention_mask=inputs["attention_mask"]
            )

        # Use the processor to convert the token IDs into text
        # The processor takes the token IDs and returns the corresponding text
        transcription_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        # Return the transcription text
        return transcription_text
