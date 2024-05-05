from pathlib import Path
import os
import platform


def walk_dir(dir, include_exts=None, ignore_dirs={}):
    include_exts = None \
        if include_exts is None else \
        set(ext.lower() for ext in include_exts)

    for root, ds, fs in dir.walk():
        for d in ignore_dirs:
            if d in ds:
                ds.remove(d)
        ds.sort()
        fs.sort()
        for f in fs:
            p = root / f
            ext = p.suffix.lower()
            if include_exts is None or ext in include_exts:
                yield p


def home_dir():
    s = platform.system()
    match s.lower():
        case "darwin": return Path(os.getenv("HOME")).resolve()
        case "windows": return Path(os.getenv("USERPROFILE")).resolve()
        case _: raise NotImplementedError(f"Unsupported platform \"{s}\"")


def clean_dir(dir):
    for root, ds, _ in dir.walk(top_down=False):
        ds.sort()
        for d in ds:
            p = root / d
            print(p)
            if len(list(p.iterdir())) == 0:
                p.rmdir()
