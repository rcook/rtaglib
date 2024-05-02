from tagtagtag.artist import Artist
from tagtagtag.metadata_db import MetadataDB
from uuid import UUID


def do_db(ctx, data_dir):
    db_path = data_dir / "metadata.db"
    ctx.log_info("do_db begin")
    ctx.log_info(f"db_path={db_path}")

    with MetadataDB(db_path) as db:
        print(
            Artist.get_by_uuid(
                db=db,
                uuid=UUID("cfd0e186-c2b9-449c-9ca8-48bfd0cfae36")))

    ctx.log_info("do_db end")
