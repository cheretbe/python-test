#!/usr/bin/env python3

import argparse
import fnmatch
import os
import pathlib
import shutil
import zipfile

def check_existing_file(file_path, overwrite):
    if file_path.exists() and not overwrite:
        raise FileExistsError(
            f"File '{str(file_path)}' exists. Use --overwrite to force copying"
        )

def main():
    parser = argparse.ArgumentParser(description="Recursive copy test")
    parser.add_argument("src", help="Source directory or zip file")
    parser.add_argument("file_mask", help="File mask")
    parser.add_argument("dst", help="Destination directory (will be created if doesn't exist)")
    parser.add_argument(
        "-o", "--overwrite", action="store_true", default=False, help="Overwrite existing files"
    )
    options = parser.parse_args()

    os.makedirs(options.dst, exist_ok=True)
    dest_path = pathlib.Path(options.dst)

    source_path = pathlib.Path(options.src)
    if source_path.is_dir():
        # Python 3.5+ only. Since Python 3.4 is EOL as of March 2019, we assume it's fine
        for source_file in source_path.rglob(options.file_mask):
            relative_path = source_file.relative_to(source_path)
            dest_file = dest_path.joinpath(source_file.relative_to(source_path))
            print(relative_path)
            check_existing_file(dest_file, options.overwrite)
            # Make sure destination path exists
            os.makedirs(str(dest_file.parent), exist_ok=True)
            shutil.copy(str(source_file), str(dest_file))
    else:
        with zipfile.ZipFile(options.src, "r") as source_zip:
            items_to_extract = []
            for zip_item in source_zip.namelist():
                # fnmatch uses os.path.normcase() under the hood, so works as
                # expected depending on the OS type
                if fnmatch.fnmatch(zip_item, options.file_mask):
                    print(zip_item)
                    check_existing_file(
                        pathlib.Path(dest_path.joinpath(zip_item)),
                        options.overwrite
                    )
                    items_to_extract += [zip_item]
            source_zip.extractall(path=str(dest_path), members=items_to_extract)

if __name__ == "__main__":
    main()
