import re
import json
import os


def save_text(fn, contents):
    with open(fn, "w") as pf:
        pf.write(contents)
    return 0


def _splitter(data):
    return [i.strip() for i in data.split("|")]


# contents is a list of dictionary
def save_json(dump_file, contents):
    json_bytes = json.dumps(contents, ensure_ascii=False, indent=2).encode("utf-8")
    save_text(dump_file, json_bytes.decode())
    return


def read_file_content(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "..", "tests", "data", filename)) as fileobj:
        content = fileobj.read()
    return content


def read_json_file(filename):
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, "..", "tests", "data", filename)) as fileobj:
        json_object = json.load(fileobj)
    return json_object


def _extract_values_from_patterns(patterns, raw_attrib):
    # Extract values using regex patterns
    values = {}
    match = None
    for key, pattern in patterns.items():
        match = re.search(pattern, raw_attrib)
        if match:
            values[key] = match.group(1)
    return values
