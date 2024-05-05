from colorama import Fore
from rtag.album import Album
from rtag.artist import Artist
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.cprint import cprint
from rtag.fs import walk_dir
from rtag.metadata.metadata import Metadata
from rtag.track import Track


def move_file(source_path, target_path):
    cprint(Fore.LIGHTRED_EX, f"TBD: move {source_path} -> {target_path}")


def do_retag(ctx, input_dir, music_dir, misc_dir):
    with ctx.open_db() as db:
        for p in walk_dir(input_dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            rel_path = p.relative_to(input_dir)
            display_path = "/".join(rel_path.parts)
            cprint(Fore.LIGHTCYAN_EX, f"Processing {display_path}")

            m = Metadata.load(p)

            if m.musicbrainz_track_id is not None:
                target_path = music_dir / rel_path
                move_file(p, target_path)
                continue

            assert m.rcook_track_id is not None
            artist = Artist.get_by_uuid(db=db, uuid=m.rcook_artist_id)
            album = Album.get_by_uuid(db=db, uuid=m.rcook_album_id)
            track = Track.get_by_uuid(db=db, uuid=m.rcook_track_id)

            print(album.get_track_count(db=db))
            m.artist_title = artist.title
            m.album_title = album.title
            m.track_title = track.title
