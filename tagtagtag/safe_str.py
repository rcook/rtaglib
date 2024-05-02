from unidecode import unidecode


REPLACE_CHARS = {
    ".",
}


REPLACEMENT = "_"


KEEP_CHARS = {
    "_",
    "-"
}


def make_safe_str(s):
    output = ""
    replacing = False
    for c in unidecode(s):
        if c.isalnum() or c in KEEP_CHARS:
            output += c
            replacing = False
        elif c.isspace() or c in REPLACE_CHARS:
            if not replacing:
                output += REPLACEMENT
            replacing = True
    output = output.strip(REPLACEMENT)
    return output


def humanize_str(s):
    return s.replace("_", " ").strip()
