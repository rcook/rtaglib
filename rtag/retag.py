from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.fs import walk_dir
from rtag.metadata.metadata import Metadata


def do_retag(ctx, dir):
    with ctx.open_db():
        for p in walk_dir(dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            m = Metadata.load(p)
            if m.musicbrainz_track_id is not None:
                continue

            assert m.rcook_track_id is not None
