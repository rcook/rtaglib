from colorama import Fore
from pathlib import Path
from rtag.cprint import cprint
from rtag.metadata.metadata import Metadata
import os


def do_picard_fixup(ctx):
    def perform_fixup(path):
        m = Metadata.load(path)
        if m.musicbrainz_album_id is None:
            return False

        fixup = ctx.config.fixups_by_album_id.get(m.m.musicbrainz_album_id)
        if not fixup:
            return False

        if ctx.dry_run:
            cprint(
                Fore.LIGHTYELLOW_EX,
                f"Skipping {m.album_title} in dry-run mode")
            return True

        fixed_up = False

        if m.album_title != fixup.album_title_tag_override:
            fixed_up = True
            cprint(
                Fore.LIGHTYELLOW_EX,
                f"Fixing album tag from {m.album_title} -> {fixup.album_title_tag_override}")
            m.album_title = fixup.album_title_tag_override
            m.save()

        if path.parent.name != fixup.dir:
            fixed_up = True
            source_pretty = str(path.parent.name) + "/" + path.name
            target_pretty = str(fixup.dir) + "/" + path.name
            cprint(
                Fore.LIGHTYELLOW_EX,
                f"Renaming {source_pretty} -> {target_pretty}")

            target_dir = path.parent.parent.joinpath(fixup.dir)
            target_path = target_dir.joinpath(path.name)

            os.makedirs(target_dir, exist_ok=True)
            os.rename(path, target_path)
            if len(os.listdir(path.parent)) == 0:
                os.rmdir(path.parent)

        return fixed_up

    total = 0
    fixup_count = 0
    for d0, dir_names, fs in os.walk(ctx.config.root_dir):
        dir_names.sort()
        fs.sort()
        d1 = Path(d0)
        for f in fs:
            if os.path.splitext(f)[1].lower() not in ctx.config.skips and f not in ctx.config.skips:
                p = d1.joinpath(f)
                total += 1
                path_pretty = str(p.relative_to(ctx.config.root_dir)).replace(
                    "\\",
                    "/")
                cprint(
                    Fore.LIGHTBLUE_EX,
                    f"{total:,}".rjust(8),
                    Fore.LIGHTMAGENTA_EX,
                    "  ",
                    path_pretty,
                    sep="")

                if perform_fixup(path=p):
                    fixup_count += 1

    cprint(
        Fore.GREEN,
        f"Files processed: {total}; files fixed up: {fixup_count}")
