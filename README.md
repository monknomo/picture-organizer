# picture-organizer
Python script that organizes photos

Usage: `python organizer src dest`  Optional `--dedupe` and `--report` flags.

Moves picture files from src directory to dest directory.  Organizes in folder structure `dest/YYYY/MON/picture.ext` based on picture EXIF data.  Files with no EXIF data are put in `dest/no-exif-data`  Files with no EXIF date are put in `dest/no-exif-date`.

--dedupe compares files in dest directory and, when identical hashes are found, removes all but one identical file.

--report outputs a report of the files moved, including number, file names and sizes.
