from dataclasses import dataclass


@dataclass(frozen=True)
class IndexOfTotal:
    index: int | None
    total: int | None

    @classmethod
    def convert(cls, obj):
        match obj:
            case int(index):
                return cls(index=index, total=None)
            case (int(index), int(total)):
                return cls(index=index, total=total)
            case str(s):
                match s.split("/", maxsplit=1):
                    case [index_str]: return cls(index=int(index_str), total=None)
                    case [index_str, total_str]: return cls(index=int(index_str), total=int(total_str))
                    case _: raise NotImplementedError()
            case _: raise NotImplementedError()
