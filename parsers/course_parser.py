from parsers.utils import _extract_values_from_patterns

# Define regex patterns for each value
course_pattern = {
    "language": r"(\w+)",
    "format": r"(MP4|MKV|MP4,MKV|MP4,MKV)",
    "resolution": r"(AVC \d+([Ã—×]|x|\d+)+)",
    "audio": r"(AAC \w+.\w+)",
    "duration": r"\|([^|]+(?i:lectures|lessons)[^|]+)\|",
    "size": r"(\d+(?:\.\d+)? [GM]B)",
}


def parse_course_metadata(raw_json_data):
    title = raw_json_data.get("item_title")
    url = raw_json_data.get("item_url")
    posted = raw_json_data.get("item_post_date")

    values = _extract_values_from_patterns(
        course_pattern, raw_json_data.get("item_attribs")
    )

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
