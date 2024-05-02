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
