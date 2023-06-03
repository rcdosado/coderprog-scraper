from parsers.utils import _extract_values_from_patterns

book_pattern = {
    "language": r"(\w+)",
    "year": r"(\d{4})",
    "ISBN": r"ISBN: ([\d-]+)",
    "pages": r"(\d+) Pages",
    "formats": r"(PDF|EPUB|PDF,EPUB|EPUB,PDF)",
    "size": r"(\d+ MB)",
}


def parse_book_metadata(json_data):
    title = json_data.get("item_title")
    url = json_data.get("item_url")
    post_date = json_data.get("item_post_date")

    # Define regex patterns for each value
    # Extract values using regex patterns

    values = _extract_values_from_patterns(book_pattern, json_data.get("item_attribs"))

    language = values.get("language")
    year = values.get("year")
    isbn = values.get("ISBN")
    pages = values.get("pages")
    formats = values.get("formats")
    size = values.get("size")

    return {
        "category": "books",
        "title": title,
        "url": url,
        "posted": post_date,
        "language": language,
        "published": year,
        "isbn": isbn,
        "num_pages": pages,
        "types_available": formats,
        "size": size,
    }
