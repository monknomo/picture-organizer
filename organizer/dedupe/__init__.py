import os
from itertools import product
from os.path import join

def md5_for_file(f, block_size=2**20):
    """
    Reads in a file, f, using a configurable block size, block_size.

    Returns an md5 hash of the content of the file
    """
    m = hashlib.md5()
    with open(f , "rb" ) as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()

def deduplicate_directory(target):
    """
    Recursively walks the target directory and removes all but one copy of files 
    that share an md5 hash
    """
    dedupe_walk = os.walk(target)
    dupes = {}
    for w in dedupe_walk:
        src_files = product([w[0]], w[2])
        for file in src_files:
            target = join(file[0], file[1])
            hash = md5_for_file(join(file[0], file[1]))
            try:
                dupes[hash].append((target, os.stat(target).st_size))
            except KeyError:
                dupes[hash] = []
                dupes[hash].append((target, os.stat(target).st_size))    
    for key in dupes.keys():
        for file, size in dupes[key][1:]:
            os.remove(file)
        if 0 == size:
            os.remove(dupes[key][0])
    return dupes