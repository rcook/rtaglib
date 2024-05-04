from dataclasses import dataclass
from functools import cache


@dataclass(frozen=True)
class Pos:
    index: int
    total: int | None

    @classmethod
    def check(cls, obj):
        assert isinstance(obj, cls)
        return obj

    @classmethod
    def parse(cls, s):
        match s.split("/", maxsplit=1):
            case [index_str]: return cls(index=int(index_str), total=None)
            case [index_str, total_str]: return cls(index=int(index_str), total=int(total_str))
            case _: raise NotImplementedError()

    @cache
    def __str__(self):
        if self.total is None:
            return str(self.index)
        else:
            return f"{self.index}/{self.total}"
