from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from uuid import UUID
import yaml


@dataclass(frozen=True)
class Fixup:
    album_id: UUID
    dir: str
    album_title_tag_override: str

    @classmethod
    def read(cls, obj):
        return cls(
            album_id=UUID(obj["album_id"]),
            dir=obj["dir"],
            album_title_tag_override=obj["album_title_tag_override"])


@dataclass(frozen=True)
class Retagging:
    music_dir: Path
    misc_dir: Path

    @classmethod
    def read(cls, obj):
        return cls(
            music_dir=Path(obj["music_dir"]),
            misc_dir=Path(obj["misc_dir"]))


class Config:
    @classmethod
    def load(cls, path):
        with open(path, "rt") as f:
            obj = yaml.load(f, Loader=yaml.SafeLoader)
        return cls(path=path, obj=obj)

    def __init__(self, path, obj):
        self._path = path
        self._obj = obj

    @cached_property
    def root_dir(self):
        return Path(
            self._path,
            "..",
            self._obj["root_dir"]).resolve()

    @cached_property
    def skips(self): return set(str(x) for x in self._obj.get("skips", []))

    @cached_property
    def fixups_by_album_id(self):
        fixups = [Fixup.read(x) for x in self._obj["fixups"]]
        return {
            f.album_id: f
            for f in fixups
        }

    @cached_property
    def retagging(self): return Retagging.read(self._obj["retagging"])
