from parsers.utils import  _extract_values_from_patterns

def parse_course(json_data):
    title = json_data.get("item_title")
    url = json_data.get("item_url")
    posted = json_data.get("item_post_date")

    # Define regex patterns for each value
    patterns = {
        "language": r"(\w+)",
        "format": r"(MP4|MKV|MP4,MKV|MP4,MKV)",
        "resolution": r"(AVC \w+.\w+)",
        "audio": r"(AAC \w+.\w+)",
        "duration": r"\|([^|]+(?i:lectures|lessons)[^|]+)\|",
        "size": r"(\d+(?:\.\d+)? [GM]B)",
    }

    # Extract values using regex patterns
    values = _extract_values_from_patterns(patterns, json_data.get("item_attribs"))

    language = values.get("language")
    file_type = values.get("format")
    resolution = values.get("resolution")
    audio = values.get("audio")
    duration = values.get("duration").strip() if (values.get("duration")) else "None"
    size = values.get("size")

    return {
        "category": "tutorial",
        "title": title,
        "url": url,
        "posted": posted,
        "language": language,
        "file_type": file_type,
        "resolution": resolution,
        "audio": audio,
        "duration": duration,
        "size": size,
    }
