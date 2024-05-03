from dataclasses import dataclass


@dataclass(frozen=True)
class Context:
    dry_run: bool

    @classmethod
    def from_args(cls, args):
        return cls(dry_run=args.dry_run)
