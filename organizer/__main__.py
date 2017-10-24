from move_files import move_files   
from dedupe import md5_for_file, deduplicate_directory 
import click
import pprint

@click.command()
@click.argument('src', type=click.Path(exists=True))
@click.argument('dest', type=click.Path(exists=False))  
@click.option('--dedupe', default=False, is_flag=True, 
    help="de-duplicate destination folder")    
@click.option('--report', default=False, is_flag=True, 
    help="print a progress report at script completion")      
def move_all(src, dest, dedupe, report):
    """
    Command line method.  Takes src dest as required arguments.  Optionally 
    takes --dedupe as a flag.  When --dedupe is present, will de-deuplicate the
    dest directory
    """ 
    files_moved, files_not_moved = move_files(src,dest)
    if report:
        print("##########")
        print("NUM FILES CONSIDERED")
        print("##########")
        print(str(len(files_moved) + len(files_not_moved)))
        print("##########")
        print("NUM FILES MOVED")
        print("##########")
        print(str(len(files_moved)))
        print("##########")
        print("FILES MOVED")
        print("##########")
        print(files_moved)
        print("##########")
        print("FILES NOT MOVED")
        print("##########")
        print(files_not_moved)
        print("##########")
    if dedupe:
        dupe_list = deduplicate_directory(dest)  
        if report:
            print("DUPLICATE FILE REPORT")        
            print("##########")            
            total = 0
            num_duplicates = 0
            pprint.PrettyPrinter(indent=2).pprint(dupe_list)
            print("##########")
            print("TOTAL SIZE OF DUPLICATE FILES IN BYTES")
            print("##########")
            for key in dupe_list.keys():
                if len(dupe_list[key]) > 1:
                    total += dupe_list[key][0][1] * len(dupe_list[key])
                    num_duplicates += len(dupe_list[key])
            print(str(total))
            print("##########")
            print("NUMBER DUPLICATES REMOVED")
            print("##########")
            print(str(num_duplicates))
            print("##########")
            print("NUMBER DUPLICATES")
            print("##########")
            print(str(num_duplicates + len(dupe_list.keys())))
            print("##########")

if __name__ == '__main__':
    move_all()