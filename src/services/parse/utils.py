from urllib.parse import urlparse, unquote
import os

from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    TokenClassificationPipeline,
    pipeline,
)

from transformers.pipelines import AggregationStrategy
import numpy as np


def get_filename_from_cd(cd):
    """
    Extract filename from content-disposition header if available.
    """
    if not cd or "filename=" not in cd:
        return None
    fname = cd.split("filename=")[1].split(";")[0]
    if fname.lower().startswith(("'", '"')):
        fname = fname[1:-1]
    return unquote(fname)


def generate_filename_from_url(url):
    """
    Extract filename from URL if possible.
    """
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)


class TextProcessingPipeline:
    """
    A pipeline for processing text, including extracting key phrases and summarizing text.
    """

    def __init__(self):
        """
        Initializes the TextProcessingPipeline.
        """
        self.keyphrase_extractor = None
        self.summarizer = None

    async def extract_tags(self, response_list, key):
        """
        Extracts key phrases from a list of responses.

        Args:
            response_list (list): A list of responses.
            key (str): The key to use to extract the text from the responses.

        Returns:
            list: A list of key phrases.
        """
        # Initialize the keyphrase extractor if it hasn't been initialized yet
        if self.keyphrase_extractor is None:
            model_name = "ml6team/keyphrase-extraction-kbir-inspec"
            self.keyphrase_extractor = KeyphraseExtractionPipeline(model=model_name)

        # Combine all the responses into a single string
        massive_text = " ".join([response.get(key, "") for response in response_list])

        # Extract the key phrases
        tags = self.keyphrase_extractor(massive_text)

        return tags.tolist()

    async def summarize(self, response_list, key):
        """
        Summarizes a list of responses.

        Args:
            response_list (list): A list of responses.
            key (str): The key to use to extract the text from the responses.

        Returns:
            str: The summarized text.
        """
        # Initialize the summarizer if it hasn't been initialized yet
        if self.summarizer is None:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        # Combine all the responses into a single string
        massive_text = " ".join([response.get(key, "") for response in response_list])

        # Summarize the text
        return self.summarizer(
            massive_text, max_length=150, min_length=30, do_sample=False
        )


class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    """
    A pipeline for extracting key phrases from text.
    """

    def __init__(self, model, *args, **kwargs):
        """
        Initializes the KeyphraseExtractionPipeline.

        Args:
            model (str): The name of the model to use for key phrase extraction.
        """
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, all_outputs):
        """
        Postprocesses the outputs of the key phrase extraction.

        Args:
            all_outputs (list): The outputs of the key phrase extraction.

        Returns:
            list: The postprocessed key phrases.
        """
        # Postprocess the outputs
        results = super().postprocess(
            all_outputs=all_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )

        # Return the unique key phrases
        return np.unique([result.get("word").strip() for result in results])
