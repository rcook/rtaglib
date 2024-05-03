from unidecode import unidecode


KEEP_CHARS = {"-"}
REPLACE_CHARS = {"."}
PLACEHOLDER = "_"


def make_safe_str(s):
    output = ""
    replacing = False
    for c in unidecode(s):
        if c.isalnum() or c in KEEP_CHARS:
            output += c
            replacing = False
        elif c.isspace() or c == PLACEHOLDER or c in REPLACE_CHARS:
            if not replacing:
                output += PLACEHOLDER
                replacing = True
    output = output.strip(PLACEHOLDER)
    return output


def humanize_str(s):
    return s.replace("_", " ").strip()
