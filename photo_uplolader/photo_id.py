import re


def extract_photo_id(current_url):
    pattern = r'KSP_\d+_\d+'
    return re.findall(pattern, current_url)[0]



