import os
from itertools import product
from os.path import join, basename, dirname, splitext
from shutil import  copyfileobj, copystat
import exifread
import arrow
import click

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """
    Takes an integer and returns a string representation of the base36 value of that
    integer
    """
    base36 = ''
    sign = ''
    
    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def safe_copy(src, dest, uniq):
    """
    Takes a src file location and a dest file location and a unique, incrementable
    identifier.

    Copies the src file to the dest file.  If the dest file already exists, the uniq
    identifier is appended to the filename in base36 form, speparated from the
    filename with an underscore.

    E.G.

    "my-file-name.txt" will turn into "my-file-name_1.txt", rather than overwriting
    the existing file
    """
    try:
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, 'wb') as f:
            with open(src, 'rb') as sf:
                copyfileobj(sf,f)
                copystat(src, dest)
    except FileExistsError:
        new_filename = splitext(dest)[0]\
            +"_"+base36encode(uniq)+splitext(dest)[1]
        uniq += 1
        return safe_copy(src, new_filename, uniq)
    return uniq        

def get_dest_file(src_file):
    """
    Takes a src file location

    Returns the destination file location.

    In the case of files with exif data, the destination file location is the 
    year/month/filename
    
    In the case of files with exif data, but no Image DateTime, the destination
    file location is no-exif-date/filename

    In the case of files without exif data, the destination file is 
    no-exif-data/filename
    """
    tags = {}
    with open(src_file, 'rb') as f:
        try:
            tags = exifread.process_file(f, details=False, stop_tag='Image DateTime', strict=True)
        except Exception:
            print(src_file)
            return join('corrupted-exif-data', basename(src_file))
    if tags:
        try:
            picture_time = arrow.get(str(tags['Image DateTime']), 
                                        'YYYY:MM:DD HH:mm:ss')
            picture_year = str(picture_time.year)
            picture_month = arrow.get(str(picture_time.month), 'M')\
                .format('MMMM')     
            return join(picture_year, picture_month, basename(src_file))
        except KeyError:
            return  join('no-exif-date', basename(src_file))
    else:
        return join('no-exif-data', basename(src_file))

def transform_to_src_dest(src_dir, file, dest_dir):
    """
    Takes the source directory, a file and the dest directory

    Returns a tuple of the form 
    (fully-qualified-src-file, full-qualified-dest-file)
    """
    return ( join(src_dir,file)\
        , join( dest_dir, get_dest_file( join( src_dir, file ) ) ) )

def is_ini(file):
    """
    Returns True if file has a '.ini' extension
    """
    return splitext(file[1])[1] != '.ini'

def move_files(src, dest):
    """
    Moves all files in src directory to dest directory

    Files with exif data are moved to dest/year/month/file

    Files without exif dates are moved to dest/no-exif-date/file

    Files without exif data are moved to dest/no-exif-data/file
    """
    uniq = 1
    files_moved = []
    files_not_moved = []
    dir_walk = os.walk(src)
    for w in dir_walk:
        src_files = product([w[0]], w[2])
        cnt_files = product([w[0]], w[2])
        no_ini_files = product([w[0]], w[2])
        src_files = filter(is_ini,src_files)  
        no_ini_files = filter(is_ini, no_ini_files)
        files_not_moved = list(set(cnt_files).difference(set(no_ini_files)))
        for blah in [transform_to_src_dest(f[0],f[1], dest) for f in src_files]:  
            os.makedirs(dirname(blah[1]), exist_ok=True)
            uniq = safe_copy(blah[0], blah[1], uniq)    
            files_moved.append(blah[0] )
    return (files_moved, files_not_moved)