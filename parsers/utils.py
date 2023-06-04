import re
import json
import os


def save_text(fn, contents):
    with open(fn, "w") as pf:
        pf.write(contents)
    return 0


def _splitter(data):
    return [i.strip() for i in data.split("|")]


def read_file_content(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "..", "tests", "data", filename)) as fileobj:
        content = fileobj.read()
    return content


def _extract_values_from_patterns(patterns, json_string):
    # Extract values using regex patterns
    values = {}
    match = None
    for key, pattern in patterns.items():
        match = re.search(pattern, json_string)
        if match:
            values[key] = match.group(1)
    return values
