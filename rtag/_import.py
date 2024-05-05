from dataclasses import asdict, dataclass, fields
from rtag.album import Album
from rtag.artist import Artist
from rtag.constants import MUSIC_IGNORE_DIRS, MUSIC_INCLUDE_EXTS
from rtag.fs import walk_dir
from rtag.inferred_info import InferredInfo
from rtag.metadata.metadata import Metadata
from rtag.metadata_db import MetadataDB
from rtag.safe_str import make_safe_str
from rtag.track import Track


@dataclass
class DBResult:
    total: int
    skipped_count: int
    new_artist_count: int
    existing_artist_count: int
    new_album_count: int
    existing_album_count: int
    new_track_count: int
    existing_track_count: int

    @classmethod
    def default(cls):
        return cls(**{f.name: 0 for f in fields(cls)})


def do_import(ctx, music_dir, init=False, new_ids=False):
    result = DBResult.default()
    with ctx.open_db(init=init) as db:
        for p in walk_dir(music_dir, include_exts=MUSIC_INCLUDE_EXTS, ignore_dirs=MUSIC_IGNORE_DIRS):
            result.total += 1
            m = Metadata.load(p)

            if m.musicbrainz_track_id is not None:
                result.skipped_count += 1
                continue

            if not new_ids and m.rcook_track_id is not None:
                result.skipped_count += 1
                continue

            process_file(
                ctx=ctx,
                result=result,
                dir=music_dir,
                path=p,
                m=m,
                db=db)

    for k, v in asdict(result).items():
        ctx.log_info(f"{k}={v}")


def process_file(ctx, result, dir, path, m, db):
    rel_path = path.relative_to(dir)
    inferred = InferredInfo.parse(rel_path)

    def get_titles(key):
        temp = getattr(m, key)
        if temp is None:
            return getattr(inferred, key), getattr(inferred, key.replace("title", "safe_title"))
        else:
            return temp, make_safe_str(temp)

    artist_title, artist_safe_title = get_titles("artist_title")
    album_title, album_safe_title = get_titles("album_title")
    track_title, track_safe_title = get_titles("track_title")
    track_disc = inferred.track_disc if m.track_disc is None else m.track_disc
    track_number = inferred.track_number if m.track_number is None else m.track_number

    artist = Artist.query(db=db, title=artist_title, default=None)
    if artist is None:
        artist = Artist.create(
            db=db,
            title=artist_title,
            safe_title=artist_safe_title)
        ctx.log_info(f"New artist: {artist.title} ({artist.uuid})")
        result.new_artist_count += 1
    else:
        result.existing_artist_count += 1

    album = Album.query(
        db=db,
        artist_id=artist.id,
        title=album_title,
        default=None)
    if album is None:
        album = Album.create(
            db=db,
            artist_id=artist.id,
            title=album_title,
            safe_title=album_safe_title)
        ctx.log_info(f"New album: {album.title} ({album.uuid})")
        result.new_album_count += 1
    else:
        result.existing_album_count += 1

    track = Track.query(
        db=db,
        album_id=album.id,
        title=track_title,
        disc=track_disc.index,
        number=track_number.index,
        default=None)
    if track is None:
        track = create_track(
            db=db,
            inferred=inferred,
            album=album,
            track_title=track_title,
            track_safe_title=track_safe_title,
            track_disc=track_disc,
            track_number=track_number)
        result.new_track_count += 1

        m.rcook_artist_id = artist.uuid
        m.rcook_album_id = album.uuid
        m.rcook_track_id = track.uuid
        # del m.rcook_artist_id
        # del m.rcook_album_id
        # del m.rcook_track_id
        m.save()
    else:
        result.existing_track_count += 1


def create_track(db, inferred, album, track_title, track_safe_title, track_disc, track_number):
    def do_create(track_disc, track_number, fail_ok=False):
        m = getattr(Track, "try_create" if fail_ok else "create")
        return m(
            db=db,
            album_id=album.id,
            title=track_title,
            safe_title=track_safe_title,
            disc=track_disc.index,
            number=track_number.index)

    if track_number is None:
        return do_create(track_disc=inferred.track_disc, track_number=inferred.track_number)

    if inferred.track_number is None:
        return do_create(track_disc=track_disc, track_number=track_number)

    if inferred.track_number == track_number:
        return do_create(track_disc=track_disc, track_number=track_number)

    track = do_create(
        track_disc=inferred.track_disc,
        track_number=inferred.track_number,
        fail_ok=True)
    if track is not None:
        return track

    return do_create(track_disc=track_disc, track_number=track_number)
