from dataclasses import dataclass
from rtag.error import ReportableError
from rtag.pos import Pos
from rtag.safe_str import humanize_str, make_safe_str
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
    track_disc: Pos
    track_number: Pos

    _TRACK_DISC_NUMBER_RE = re.compile(
        "^(?P<disc>\\d+)\\-(?P<number>\\d+)[ \\-_](?P<rest>.+)$")
    _TRACK_NUMBER_RE = re.compile("^(?P<number>\\d+)[ \\-_](?P<rest>.+)$")

    @classmethod
    def parse(cls, rel_path):
        def strip_track_disc_number(s):
            if m := cls._TRACK_DISC_NUMBER_RE.match(s):
                track_disc = int(m.group("disc"))
                track_number = int(m.group("number"))
                track_safe_title = m.group("rest")
            elif m := cls._TRACK_NUMBER_RE.match(s):
                track_disc = None
                track_number = int(m.group("number"))
                track_safe_title = m.group("rest")
            else:
                track_disc = None
                track_number = None
                track_safe_title = s
            return Pos(index=track_disc, total=None), Pos(index=track_number, total=None), track_safe_title.lstrip("_-. ")

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
