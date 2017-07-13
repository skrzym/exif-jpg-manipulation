import os
import re
import argparse

# Code Source: https://stackoverflow.com/questions/21355316/getting-metadata-for-mov-video

import datetime
import struct

parser = argparse.ArgumentParser(description="EXPERIMENTAL! WARNING THIS WILL CHANGE ALL FOUND .MOV FILENAMES! EXPERIMENTAL! This will rename all .MOV files in a directory to follow the following capture time format 'MOV_YYYYMMDD_HHMMSS.MOV'. If a conflict arises the script will increment the file name by 1 as such 'MOV_YYYYMMDD_HHMMSS_1.MOV'.")
parser.add_argument('--path', help="file directory to look for MOV files to modify")
parser.add_argument('--days', type=int, default=0, help="integer value adjusts datetime 'day' value")
parser.add_argument('--hours', type=int, default=0, help="integer value adjusts datetime 'hour' value")
parser.add_argument('--minutes', type=int, default=0, help="integer value adjusts datetime 'minute' value")
parser.add_argument('--seconds', type=int, default=0, help="integer value adjusts datetime 'second' value")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="when set, output shows old and new file names for each modified file")
args = parser.parse_args()


def get_mov_datetime(filename):
    ATOM_HEADER_SIZE = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    EPOCH_ADJUSTER = 2082844800

    #if len(sys.argv) < 2:
    #    print "USAGE: mov-length.py <file.mov>"
    #    sys.exit(1)

    # open file and search for moov item
    f = open(filename, "rb")
    while 1:
        atom_header = f.read(ATOM_HEADER_SIZE)
        if atom_header[4:8] == 'moov':
            break
        else:
            atom_size = struct.unpack(">I", atom_header[0:4])[0]
            f.seek(atom_size - 8, 1)

    # found 'moov', look for 'mvhd' and timestamps
    atom_header = f.read(ATOM_HEADER_SIZE)
    if atom_header[4:8] == 'cmov':
        print "moov atom is compressed"
        return None
    elif atom_header[4:8] != 'mvhd':
        print "expected to find 'mvhd' header"
        return None
    else:
        f.seek(4, 1)
        creation_date = struct.unpack(">I", f.read(4))[0]
        #modification_date = struct.unpack(">I", f.read(4))[0]
        #print "creation date:",
        #print datetime.datetime.utcfromtimestamp(creation_date - EPOCH_ADJUSTER)
        #print "modification date:",
        #print datetime.datetime.utcfromtimestamp(modification_date - EPOCH_ADJUSTER)
        return datetime.datetime.utcfromtimestamp(creation_date - EPOCH_ADJUSTER) + datetime.timedelta(days=args.days,hours=args.hours,minutes=args.minutes,seconds=args.seconds)


def list_dir_mov(basedir=os.path.curdir):
    mov_files = []
    other_files = []
    sub_dirs = []
    for item in os.listdir(basedir):
        abs_path = os.path.join(basedir,item)
        if os.path.isfile(abs_path):
            if re.search('(\.MOV)',item):
                mov_files.append(abs_path)
            else:
                other_files.append(abs_path)
        else:
            sub_dirs.append(abs_path)
    return (mov_files,other_files,sub_dirs)


def modify_mov_filename(directory=os.curdir):
    movs,others,subdirs = list_dir_mov(directory)
    for mov in movs:
            oldmov = mov[:-4]+'_old'+mov[-4:]
            os.rename(mov,oldmov)
    movs,others,subdirs = list_dir_mov(directory)

    print '=MOV-FILENAME-MODIFIER'+ '='*17
    print 'Ignored files:', len(others)
    print 'Ignored sub directories:', len(subdirs)
    print 'MOVs files to be edited:', len(movs)
    print '='*40
    if len(movs) == 0:
        print 'There are no "*.MOV" files in supplied directory!'
        print '='*40
    else:
        print 'MOV timestamp to be offset as follows:'
        print 'Days:'+str(args.days)+'|'+'Hours:'+str(args.hours)+'|'+'Minutes:'+str(args.minutes)+'|'+'Seconds:'+str(args.seconds)
        print '='*40
        print 'Editing MOV Filenames...'

        for mov in movs:

            # fdt = datetime.datetime.strptime(piexif.load(mov)['0th'][306],"%Y:%m:%d %H:%M:%S")
            fdt = get_mov_datetime(mov)

            matches = [
                item
                for item in os.listdir(directory)
                if re.search('MOV_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'(_?[0-9]*)\.[mM][oO][vV]', item)
            ]
            if len(matches) > 0:
                if os.path.basename(mov) != 'MOV_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.MOV':
                    new_filename = 'MOV_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'_'+str(len(matches))+'.MOV'
            else:
                new_filename = 'MOV_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.MOV'

            try:
                os.rename(mov,directory+'\\'+new_filename)
            except WindowsError, arg:
                print(os.path.basename(mov),new_filename)
                raise WindowsError, arg
            if args.verbose:
                print ' '*2 + os.path.basename(mov)[:-8] + ' --> ' + new_filename[:-4]
        print '='*40
        print 'Editing Complete!', str(len(movs)), 'files modified.'
        print '='*40


modify_mov_filename(directory=args.path)
