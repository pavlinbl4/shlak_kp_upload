import re

def extract_photo_id(current_url: str) -> str:
    """
    Extracts the photo ID from the current URL.
    Args:
        current_url (str): The URL string from which to extract the photo ID.
    Returns:
        str: The extracted photo ID.
    """
    pattern = r'KSP_\d+_\d+'
    return re.findall(pattern, current_url)[0]



