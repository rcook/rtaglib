from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.fs import walk_dir
from rtag.metadata.metadata import Metadata


def move_file(source_path, target_path):
    print(source_path)
    print(target_path)
    exit(0)
    pass


def do_retag(ctx, input_dir, music_dir, misc_dir):
    print(music_dir)
    print(misc_dir)
    with ctx.open_db():
        for p in walk_dir(input_dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            rel_path = p.relative_to(input_dir)
            display_path = "/".join(rel_path.parts)
            m = Metadata.load(p)
            if m.musicbrainz_track_id is not None:
                target_path = music_dir / rel_path
                move_file(p, target_path)
                continue

            assert m.rcook_track_id is not None
