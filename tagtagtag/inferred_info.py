from dataclasses import dataclass
from tagtagtag.error import ReportableError
from tagtagtag.safe_str import humanize_str, make_safe_str
import os
import re


@dataclass(frozen=True)
class InferredInfo:
    artist_title: str
    artist_safe_title: str
    album_title: str
    album_safe_title: str
    track_title: str
    track_safe_title: str
    track_number: int

    _FILE_NAME_RE = re.compile("^(?P<digits>\\d+)(?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        parts = rel_path.parts
        if len(parts) < 3:
            raise ReportableError(
                f"File path \"{rel_path}\" does not match expected structure")

        artist_safe_title, album_safe_title, file_name = parts[-3:]

        base_file_name, _ = os.path.splitext(file_name)
        m = cls._FILE_NAME_RE.match(base_file_name)
        if m is None:
            track_number = None
            track_safe_title = base_file_name
        else:
            track_number = int(m.group("digits"))
            track_safe_title = m.group("rest").lstrip("_").lstrip(" ")

        return cls(
            artist_title=humanize_str(artist_safe_title),
            artist_safe_title=make_safe_str(artist_safe_title),
            album_title=humanize_str(album_safe_title),
            album_safe_title=make_safe_str(album_safe_title),
            track_title=humanize_str(track_safe_title),
            track_safe_title=make_safe_str(track_safe_title),
            track_number=track_number)
