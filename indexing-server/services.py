import logging
import os
from typing import List, Tuple, Union, Optional
import mimetypes
from pathlib import Path

# Document processing imports
import PyPDF2
import docx
from litellm import completion, acompletion, embedding
import litellm
import base64

from fastapi import HTTPException, status
from config import settings
from constants import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE, MAX_TEXT_LENGTH, CHUNK_SIZE
from prompts import (
    get_summary_prompt,
    get_chunk_summary_prompt,
    get_final_summary_prompt,
    get_image_content_prompt,
)

logger = logging.getLogger(settings.app_name)

# Constants for logging truncation
MAX_LOG_LENGTH = 200
VECTOR_LOG_LENGTH = 50

# Image file extensions that support vision processing
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".svg"}


def setup_online_model_env():
    """Set up environment variables for online model API keys."""
    if settings.use_online_models and settings.gemini_api_key:
        # Set environment variable for LiteLLM to use Gemini
        os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key
        logger.debug("Set GOOGLE_API_KEY environment variable for online models")


def truncate_for_log(text: str, max_length: int = MAX_LOG_LENGTH) -> str:
    """Truncate text for logging to avoid log spam."""
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}... ({len(text)} chars total)"


def truncate_vector_for_log(
    vector: List[float], max_length: int = VECTOR_LOG_LENGTH
) -> str:
    """Truncate vector for logging."""
    if len(vector) <= max_length:
        return str(vector)
    return f"[{', '.join(f'{v:.4f}' for v in vector[:max_length])}... ] ({len(vector)} dims)"


def validate_file_type(file_path: str) -> Tuple[bool, str]:
    """
    Validate if the file type is supported for indexing.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_supported, mime_type)
    """
    file_extension = Path(file_path).suffix.lower()

    if file_extension in SUPPORTED_FILE_TYPES:
        return True, SUPPORTED_FILE_TYPES[file_extension]

    return False, ""


def check_file_size(file_path: str) -> bool:
    """
    Check if file size is within acceptable limits.

    Args:
        file_path: Path to the file

    Returns:
        True if file size is acceptable, False otherwise
    """
    try:
        file_size = os.path.getsize(file_path)
        return file_size <= MAX_FILE_SIZE
    except OSError:
        return False


def is_image_file(file_path: str) -> bool:
    """Check if file is an image that can be processed with vision."""
    file_extension = Path(file_path).suffix.lower()
    return file_extension in IMAGE_EXTENSIONS


def encode_image_to_base64(file_path: str) -> str:
    """Encode image file to base64 for vision processing."""
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_string
    except Exception as e:
        logger.error(f"Failed to encode image {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process image file: {str(e)}",
        )


async def process_image_with_vision(file_path: str) -> str:
    """
    Process image using vision models (local or online).
    Uses content-focused prompt to extract searchable information.

    Args:
        file_path: Path to the image file

    Returns:
        Description/analysis of the image content

    Raises:
        HTTPException: If vision processing fails
    """
    try:
        logger.info(f"Processing image with vision: {truncate_for_log(file_path, 60)}")

        # Encode image to base64
        base64_image = encode_image_to_base64(file_path)

        # Use content extraction prompt
        prompt = get_image_content_prompt(file_path)

        # Create vision messages
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]

        # Choose model based on configuration
        if settings.use_online_models:
            logger.info(f"Using online vision model: {settings.online_vision_model}")
            # Set up API key for online models
            setup_online_model_env()
            model = settings.online_vision_model
            api_base = None
        else:
            logger.info(f"Using local vision model: {settings.ollama_vision_model}")
            model = f"ollama/{settings.ollama_vision_model}"
            api_base = settings.ollama_base_url

        response = await acompletion(
            model=model,
            messages=messages,
            api_base=api_base,
            temperature=0.3,
            max_tokens=1500,
        )

        description = response.choices[0].message.content.strip()

        if not description:
            logger.warning(f"Empty vision description for {file_path}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract content from image: {file_path}",
            )

        logger.info(
            f"Generated vision description ({len(description)} chars) for {truncate_for_log(file_path, 60)}"
        )
        logger.debug(f"Vision description: {truncate_for_log(description, 300)}")
        return description

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vision processing failed for {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vision processing failed: {str(e)}",
        )


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content

    Raises:
        HTTPException: If PDF processing fails
    """
    try:
        logger.debug(f"Extracting text from PDF: {truncate_for_log(file_path, 60)}")
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text_content = []

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                        logger.debug(
                            f"Extracted text from PDF page {page_num + 1}: {len(page_text)} chars"
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to extract text from PDF page {page_num + 1}: {e}"
                    )
                    continue

            if not text_content:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Unable to extract text from PDF file",
                )

            full_text = "\n\n".join(text_content)
            logger.info(
                f"Successfully extracted {len(full_text)} chars from {len(text_content)} PDF pages"
            )
            return full_text

    except Exception as e:
        logger.error(f"PDF processing failed for {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process PDF file: {str(e)}",
        )


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from a DOCX file.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted text content

    Raises:
        HTTPException: If DOCX processing fails
    """
    try:
        logger.debug(f"Extracting text from DOCX: {truncate_for_log(file_path, 60)}")
        doc = docx.Document(file_path)
        text_content = []

        for para_num, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip():
                text_content.append(paragraph.text)

        if not text_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text from DOCX file",
            )

        full_text = "\n\n".join(text_content)
        logger.info(
            f"Successfully extracted {len(full_text)} chars from {len(text_content)} DOCX paragraphs"
        )
        return full_text

    except Exception as e:
        logger.error(f"DOCX processing failed for {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process DOCX file: {str(e)}",
        )


def read_text_file(file_path: str) -> str:
    """
    Read content from a text file with multiple encoding attempts.

    Args:
        file_path: Path to the text file

    Returns:
        File content as string

    Raises:
        HTTPException: If file cannot be read
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    logger.debug(f"Reading text file: {truncate_for_log(file_path, 60)}")

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                content = file.read()
                logger.debug(
                    f"Successfully read file {truncate_for_log(file_path, 40)} with encoding {encoding}"
                )
                return content
        except UnicodeDecodeError:
            continue

    # If all encodings fail, try binary mode with error handling
    try:
        with open(file_path, "rb") as file:
            content_bytes = file.read()
            content = content_bytes.decode("utf-8", errors="replace")
            logger.warning(
                f"Read file {truncate_for_log(file_path, 40)} with error replacement"
            )
            return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file {file_path}: {str(e)}",
        )


async def read_file_content(file_path: str) -> str:
    """
    Read and extract content from a file based on its type.
    Supports text files, PDFs, DOCX, and images (with vision processing).

    Args:
        file_path: Path to the file to read

    Returns:
        The file content as a string

    Raises:
        HTTPException: If file cannot be read or processed
    """
    try:
        logger.info(f"Reading file content: {truncate_for_log(file_path, 60)}")

        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {file_path}",
            )

        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path is not a file: {file_path}",
            )

        # Validate file type
        is_supported, mime_type = validate_file_type(file_path)
        if not is_supported:
            file_extension = Path(file_path).suffix.lower()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported file type: {file_extension}. Supported types: {list(SUPPORTED_FILE_TYPES.keys())}",
            )

        # Check file size
        if not check_file_size(file_path):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes",
            )

        # Extract content based on file type
        file_extension = Path(file_path).suffix.lower()

        if is_image_file(file_path):
            # Use vision processing for images
            logger.info(f"Processing image file with vision: {file_extension}")
            content = await process_image_with_vision(file_path)
        elif file_extension == ".pdf":
            content = extract_text_from_pdf(file_path)
        elif file_extension == ".docx":
            content = extract_text_from_docx(file_path)
        else:
            # Handle as text file
            content = read_text_file(file_path)

        logger.info(
            f"Successfully processed file: {len(content)} characters extracted from {truncate_for_log(file_path, 60)}"
        )
        return content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Split text into manageable chunks for processing.

    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence or paragraph boundaries
        if end < len(text):
            # Look for sentence endings
            sentence_break = text.rfind(".", start, end)
            paragraph_break = text.rfind("\n\n", start, end)

            if paragraph_break > start + chunk_size // 2:
                end = paragraph_break + 2
            elif sentence_break > start + chunk_size // 2:
                end = sentence_break + 1

        chunks.append(text[start:end].strip())
        start = end

    logger.debug(f"Split text into {len(chunks)} chunks")
    return chunks


async def get_embedding(text: str) -> List[float]:
    """
    Get embedding from Ollama using LiteLLM.
    Fixed to properly handle the embedding response format.

    Args:
        text: Text to get embedding for

    Returns:
        Embedding vector

    Raises:
        HTTPException: If embedding generation fails
    """
    try:
        logger.debug(f"Getting embedding for text: {truncate_for_log(text)}")

        # Use LiteLLM embedding function (synchronous)
        # Note: LiteLLM embedding function is not async, so we use sync version
        import asyncio
        from functools import partial

        def _get_embedding_sync():
            return embedding(
                model=f"ollama/{settings.ollama_embedding_model}",
                input=text,  # Single text string
                api_base=settings.ollama_base_url,
            )

        # Run sync function in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, _get_embedding_sync)

        # Parse the response - LiteLLM returns EmbeddingResponse with data list of dicts
        embedding_vector = None

        try:
            # Standard LiteLLM format: response.data[0]['embedding'] (dict format)
            if hasattr(response, "data") and response.data:
                first_item = response.data[0]
                if isinstance(first_item, dict) and "embedding" in first_item:
                    embedding_vector = first_item["embedding"]
                elif hasattr(first_item, "embedding"):
                    embedding_vector = first_item.embedding
                elif isinstance(first_item, (list, tuple)):
                    embedding_vector = first_item
        except Exception as e:
            logger.error(f"Failed to parse embedding response: {e}")

        # Fallback: try as direct dict response
        if embedding_vector is None:
            try:
                if (
                    isinstance(response, dict)
                    and "data" in response
                    and response["data"]
                ):
                    data_item = response["data"][0]
                    if isinstance(data_item, dict) and "embedding" in data_item:
                        embedding_vector = data_item["embedding"]
                    elif isinstance(data_item, (list, tuple)):
                        embedding_vector = data_item
            except Exception as e:
                logger.error(f"Fallback parsing failed: {e}")

        # Final validation
        if embedding_vector is None:
            logger.error(
                f"Could not extract embedding from response type: {type(response)}"
            )
            raise ValueError("Could not extract embedding from response")

        # Validate the embedding vector
        if not isinstance(embedding_vector, (list, tuple)):
            logger.error(f"Embedding is not a list/tuple: {type(embedding_vector)}")
            raise ValueError("Embedding is not a valid vector")

        if not embedding_vector:
            logger.error("Embedding vector is empty")
            raise ValueError("Embedding vector is empty")

        # Convert to list of floats
        try:
            embedding_list = [float(x) for x in embedding_vector]
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to convert embedding to float list: {e}")
            raise ValueError("Embedding contains invalid values")

        logger.info(
            f"Generated embedding vector: {truncate_vector_for_log(embedding_list)}"
        )
        return embedding_list

    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        logger.error(f"Failed text (truncated): {truncate_for_log(text)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate embedding: {str(e)}",
        )


async def get_summary(text: str, file_path: str = "") -> str:
    """
    Get summary using local or online models based on configuration.

    Args:
        text: Text to summarize
        file_path: Optional file path for context

    Returns:
        Summary text

    Raises:
        HTTPException: If summarization fails
    """
    try:
        logger.debug(f"Getting summary for file: {file_path}")
        logger.debug(f"Input text: {truncate_for_log(text, 300)}")

        # Handle large text by chunking
        if len(text) > MAX_TEXT_LENGTH:
            logger.info(
                f"Text too long ({len(text)} chars), using chunked summarization"
            )
            return await get_chunked_summary(text, file_path)

        # Use structured prompt
        prompt = get_summary_prompt(text, file_path)
        logger.debug(f"Using prompt: {truncate_for_log(prompt, 200)}")

        # Choose model based on configuration
        if settings.use_online_models:
            logger.info(f"Using online summary model: {settings.online_summary_model}")
            # Set up API key for online models
            setup_online_model_env()
            model = settings.online_summary_model
            api_base = None
        else:
            logger.info(f"Using local summary model: {settings.ollama_summary_model}")
            model = f"ollama/{settings.ollama_summary_model}"
            api_base = settings.ollama_base_url

        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            api_base=api_base,
            temperature=0.3,
            max_tokens=1000,
        )

        summary = response.choices[0].message.content.strip()

        if not summary:
            logger.warning(f"Empty summary generated for {file_path}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate summary for {file_path}",
            )

        logger.info(f"Generated summary ({len(summary)} chars) for {file_path}")
        logger.debug(f"Summary content: {truncate_for_log(summary, 300)}")
        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary for {file_path}: {e}")
        logger.error(f"Failed text (truncated): {truncate_for_log(text, 200)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate summary: {str(e)}",
        )


async def get_chunked_summary(text: str, file_path: str = "") -> str:
    """
    Get summary for large text by processing in chunks using local or online models.

    Args:
        text: Large text to summarize
        file_path: Optional file path for context

    Returns:
        Comprehensive summary
    """
    try:
        # Split text into chunks
        chunks = chunk_text(text, MAX_TEXT_LENGTH)
        logger.info(f"Processing {len(chunks)} chunks for {file_path}")
        logger.debug(f"Original text length: {len(text)} chars")

        # Choose model based on configuration
        if settings.use_online_models:
            logger.info(
                f"Using online model for chunked summary: {settings.online_summary_model}"
            )
            # Set up API key for online models
            setup_online_model_env()
            model = settings.online_summary_model
            api_base = None
        else:
            logger.info(
                f"Using local model for chunked summary: {settings.ollama_summary_model}"
            )
            model = f"ollama/{settings.ollama_summary_model}"
            api_base = settings.ollama_base_url

        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.debug(
                f"Processing chunk {i+1}/{len(chunks)}: {truncate_for_log(chunk, 150)}"
            )

            prompt = get_chunk_summary_prompt(chunk, i + 1, len(chunks), file_path)
            logger.debug(f"Chunk {i+1} prompt: {truncate_for_log(prompt, 150)}")

            response = await acompletion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                api_base=api_base,
                temperature=0.3,
                max_tokens=500,
            )

            chunk_summary = response.choices[0].message.content.strip()
            if chunk_summary:
                chunk_summaries.append(chunk_summary)
                logger.debug(f"Chunk {i+1} summary: {truncate_for_log(chunk_summary)}")
            else:
                logger.warning(f"Empty summary for chunk {i+1} of {file_path}")

        if not chunk_summaries:
            logger.warning(f"No chunk summaries generated for {file_path}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to generate chunk summaries for {file_path}",
            )

        logger.info(
            f"Generated {len(chunk_summaries)} chunk summaries, creating final summary"
        )

        # Create final comprehensive summary
        final_prompt = get_final_summary_prompt(chunk_summaries, file_path)
        logger.debug(f"Final prompt: {truncate_for_log(final_prompt, 200)}")

        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": final_prompt}],
            api_base=api_base,
            temperature=0.3,
            max_tokens=1000,
        )

        final_summary = response.choices[0].message.content.strip()

        if not final_summary:
            # Fallback to concatenated chunk summaries
            logger.warning(
                f"Empty final summary for {file_path}, using concatenated chunks"
            )
            final_summary = "\n\n".join(chunk_summaries)
            logger.debug(f"Fallback summary: {truncate_for_log(final_summary, 200)}")

        logger.info(
            f"Generated comprehensive summary ({len(final_summary)} chars) for {file_path}"
        )
        logger.debug(f"Final summary content: {truncate_for_log(final_summary, 300)}")
        return final_summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chunked summarization for {file_path}: {e}")
        logger.error(f"Failed text (truncated): {truncate_for_log(text, 200)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate chunked summary: {str(e)}",
        )
