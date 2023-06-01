import re
def _extract_values_from_patterns(patterns, json_string):
    # Extract values using regex patterns
    values = {}
    match = None
    for key, pattern in patterns.items():
        match = re.search(pattern, json_string)
        if match:
            values[key] = match.group(1)
    return values
