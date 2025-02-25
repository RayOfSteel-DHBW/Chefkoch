from typing import List, Dict, Union

def _consume_slash(text: str, i: int) -> tuple[int, bool]:
    """
    Consumes a slash at position i.
    Recognizes either a literal slash ("/") or an encoded one ("\\u002F").
    Returns (new_index, True) if found; otherwise, (i, False).
    """
    n = len(text)
    if i < n:
        if text[i] == '/':
            return i + 1, True
        elif text[i] == '\\' and i + 5 < n and text[i:i+6] == '\\u002F':
            return i + 6, True
    return i, False

def _find_dot_html(text: str, start_index: int) -> int:
    """
    Returns the index where ".html" starts after start_index,
    or -1 if not found.
    """
    return text.find(".html", start_index)

def _parse_rs_from_index(text: str, start_index: int, id_start: int) -> Union[Dict[str, Union[Dict[str, str], int]], None]:
    """
    Given that the text at start_index begins with "rs" and immediately after "rs" 
    an encoded (or literal) slash was found (so that id_start points right after it),
    parse the pattern:
       rs[/ or \u002F][alphanumeric ID][slash][slug].html
    Returns a dict containing:
      - "data": a dict with keys "type", "full_match", "id", and "slug"
      - "end_index": index right after the parsed ".html"
    or None if parsing fails.
    """
    n = len(text)
    i = id_start

    # Parse the alphanumeric ID.
    while i < n and text[i].isalnum():
        i += 1
    if i == id_start:
        return None  # no valid ID found
    id_str = text[id_start:i]

    # Expect a slash (literal or encoded) after the ID.
    i, ok = _consume_slash(text, i)
    if not ok:
        return None

    # The slug extends until we encounter ".html".
    slug_start = i
    dot_html_index = _find_dot_html(text, i)
    if dot_html_index == -1:
        return None

    slug = text[slug_start:dot_html_index]
    full_match = text[start_index:dot_html_index+5]  # include ".html"

    return {
        "data": {
            "type": "rs",
            "full_match": full_match,
            "id": id_str,
            "slug": slug
        },
        "end_index": dot_html_index + 5
    }

def _parse_rezepte_from_index(text: str, start_index: int, id_start: int) -> Union[Dict[str, Union[Dict[str, str], int]], None]:
    """
    Given that the text at start_index begins with "rezepte" and immediately after 
    an encoded (or literal) slash was found (so that id_start points to the first character 
    of the numeric ID), parse the pattern:
       rezepte[/ or \u002F][1-16 digit ID][slash][slug].html
    Returns a dict containing:
      - "data": a dict with keys "type", "full_match", "id", and "slug"
      - "end_index": index right after ".html"
    or None if parsing fails.
    """
    n = len(text)
    i = id_start
    digits = 0

    # Parse up to 16 digits.
    while i < n and digits < 16 and text[i].isdigit():
        i += 1
        digits += 1
    if digits == 0:
        return None  # no digits found
    if i < n and text[i].isdigit():
        return None  # more than 16 digits encountered

    id_str = text[id_start:i]

    # Expect a slash.
    i, ok = _consume_slash(text, i)
    if not ok:
        return None

    slug_start = i
    dot_html_index = _find_dot_html(text, i)
    if dot_html_index == -1:
        return None

    slug = text[slug_start:dot_html_index]
    full_match = text[start_index:dot_html_index+5]

    return {
        "data": {
            "type": "rezepte",
            "full_match": full_match,
            "id": id_str,
            "slug": slug
        },
        "end_index": dot_html_index + 5
    }

def parse_urls_on_the_fly(text: str) -> List[Dict[str, str]]:
    """
    Scans the input text for URL patterns matching one of:
      1) rs[/ or \u002F][alphanumeric]/<slug>.html
      2) rezepte[/ or \u002F][1-16 digits]/<slug>.html
    This function looks for occurrences of "rs" or "rezepte" immediately followed by 
    a slash (either literal or encoded) and then parses the remainder of the URL.
    
    Returns a list of dicts with keys:
      - type: "rs" or "rezepte"
      - full_match: the full URL string (including ".html")
      - id: the extracted ID (alphanumeric or digits)
      - slug: the extracted slug
    """
    results: List[Dict[str, str]] = []
    n = len(text)
    i = 0

    while i < n:
        # Check for the "rs" pattern.
        if text.startswith("rs", i):
            j, ok = _consume_slash(text, i + 2)
            if ok:
                match_data = _parse_rs_from_index(text, i, j)
                if match_data:
                    results.append(match_data["data"])
                    i = match_data["end_index"]
                    continue

        # Check for the "rezepte" pattern.
        elif text.startswith("rezepte", i):
            j, ok = _consume_slash(text, i + len("rezepte"))
            if ok:
                match_data = _parse_rezepte_from_index(text, i, j)
                if match_data:
                    results.append(match_data["data"])
                    i = match_data["end_index"]
                    continue

        i += 1

    return results

# Example usage:
if __name__ == "__main__":
    sample_input = (
        "Some text:\n"
        "rs\\u002Fabc123\\u002FHello-World.html\n"
        "Also encoded: rs\\u002Fxyz789\\u002FSome-Recipe.html\n"
        "And: rezepte\\u002F12345\\u002FYet-Another.html\n"
        "Too long ID: rezepte\\u002F12345678901234567\\u002FWow.html"
    )
    matches = parse_urls_on_the_fly(sample_input)
    for m in matches:
        print(m)
