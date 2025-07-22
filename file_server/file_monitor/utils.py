import uuid

def generate_uuid(prefix: str) -> str:
    """
    Generate a unique id with the given prefix.
    Example: generate_uuid('file') -> 'file_abcdef123456'
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}" 