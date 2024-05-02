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
    track_disc: int
    track_number: int

    _FILE_NAME_RE = re.compile("^(?P<digits>\\d+)(?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        def strip_track_disc_number(s):
            def strip_number(s):
                m = cls._FILE_NAME_RE.match(s)
                if m is None:
                    return None, s
                else:
                    return int(m.group("digits")), m.group("rest").lstrip("_-. ")

            number0, track_safe_title = strip_number(base_file_name)
            number1, track_safe_title = strip_number(track_safe_title)
            if number1 is None:
                return None, number0, track_safe_title
            else:
                return number0, number1, track_safe_title

        parts = rel_path.parts
        if len(parts) < 3:
            raise ReportableError(
                f"File path \"{rel_path}\" does not match expected structure")

        artist_safe_title, album_safe_title, file_name = parts[-3:]
        base_file_name, _ = os.path.splitext(file_name)
        track_disc, track_number, track_safe_title = \
            strip_track_disc_number(base_file_name)

        return cls(
            artist_title=humanize_str(artist_safe_title),
            artist_safe_title=make_safe_str(artist_safe_title),
            album_title=humanize_str(album_safe_title),
            album_safe_title=make_safe_str(album_safe_title),
            track_title=humanize_str(track_safe_title),
            track_safe_title=make_safe_str(track_safe_title),
            track_disc=track_disc,
            track_number=track_number)
