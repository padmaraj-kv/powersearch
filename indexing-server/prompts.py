"""
Prompts for AI model interactions - simplified for clean output
"""


def get_summary_prompt(text: str, file_path: str = "") -> str:
    """
    Generate a summarization prompt for the given text.

    Args:
        text: The text content to summarize
        file_path: Optional file path for context

    Returns:
        Formatted prompt for summarization
    """
    file_context = f" from {file_path}" if file_path else ""

    return f"""Summarize the following text content{file_context}. Focus on main topics, key concepts, and important details. Write a comprehensive yet concise summary that captures the essence for semantic search. Return only the summary text without any labels or formatting.

{text}"""


def get_chunk_summary_prompt(
    chunk: str, chunk_number: int, total_chunks: int, file_path: str = ""
) -> str:
    """
    Generate a summarization prompt for a text chunk.

    Args:
        chunk: The text chunk to summarize
        chunk_number: Current chunk number (1-indexed)
        total_chunks: Total number of chunks
        file_path: Optional file path for context

    Returns:
        Formatted prompt for chunk summarization
    """
    file_context = f" from {file_path}" if file_path else ""

    return f"""Summarize this text chunk (part {chunk_number} of {total_chunks}){file_context}. Focus on key information and main topics in this section. Return only the summary text without any labels.

{chunk}"""


def get_final_summary_prompt(chunk_summaries: list, file_path: str = "") -> str:
    """
    Generate a prompt to create a final summary from multiple chunk summaries.

    Args:
        chunk_summaries: List of individual chunk summaries
        file_path: Optional file path for context

    Returns:
        Formatted prompt for final summarization
    """
    file_context = f" from {file_path}" if file_path else ""
    summaries_text = "\n\n".join(
        [f"Section {i+1}: {summary}" for i, summary in enumerate(chunk_summaries)]
    )

    return f"""Create a comprehensive final summary based on these section summaries{file_context}. Capture the overall content and main themes of the entire document. Return only the summary text without any labels.

{summaries_text}"""


def get_text_extraction_guidance() -> str:
    """
    Get guidance text for content extraction from different file types.

    Returns:
        Guidance text for text extraction
    """
    return """When extracting text from files:
- For code files: Include comments, docstrings, and function/class definitions
- For documents: Focus on main content, headings, and key information
- For configuration files: Include key-value pairs and important sections
- For logs: Include error messages, warnings, and significant events
- Remove excessive whitespace and formatting artifacts
- Preserve logical structure and hierarchy where possible"""
