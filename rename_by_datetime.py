import os
import datetime as dt
import re
import piexif
import argparse
from PIL.ExifTags import TAGS


parser = argparse.ArgumentParser(description="EXPERIMENTAL! WARNING THIS WILL CHANGE ALL FOUND .JPG FILENAMES! EXPERIMENTAL! This will rename all JPG files in a directory to follow the following capture time format 'IMG_YYYYMMDD_HHMMSS.JPG'. If a conflict arises the script will increment the file name by 1 as such 'IMG_YYYYMMDD_HHMMSS_1.JPG'.")
parser.add_argument('--path', help="file directory to look for JPG files to modify")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="when set, output shows old and new file names for each modified file")
args = parser.parse_args()


def list_dir_jpeg(basedir=os.path.curdir):
    jpeg_files = []
    other_files = []
    sub_dirs = []
    for item in os.listdir(basedir):
        abs_path = os.path.join(basedir,item)
        if os.path.isfile(abs_path):
            if re.search('(\.JPG)',item):
                jpeg_files.append(abs_path)
            else:
                other_files.append(abs_path)
        else:
            sub_dirs.append(abs_path)
    return (jpeg_files,other_files,sub_dirs)


def modify_jpeg_filename(directory=os.curdir):
    jpegs,others,subdirs = list_dir_jpeg(directory)
    for pic in jpegs:
            oldpic = pic[:-4]+'_old'+pic[-4:]
            os.rename(pic,oldpic)
    jpegs,others,subdirs = list_dir_jpeg(directory)

    print '=JPEG-FILENAME-MODIFIER'+ '='*17
    print 'Ignored files:', len(others)
    print 'Ignored sub directories:', len(subdirs)
    print 'JPEG files to be edited:', len(jpegs)
    print '='*40
    if len(jpegs) == 0:
        print 'There are no "*.JPG" files in supplied directory!'
        print '='*40
    else:
        print 'Editing JPEG Filenames...'

        for pic in jpegs:

            fdt = dt.datetime.strptime(piexif.load(pic)['0th'][306],"%Y:%m:%d %H:%M:%S")

            matches = [
                item
                for item in os.listdir(directory)
                if re.search('IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'(_?[0-9]*)\.[jJ][pP][gG]',item)
            ]
            if len(matches) > 0:
                if os.path.basename(pic) != 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG':
                    new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'_'+str(len(matches))+'.JPG'
            else:
                new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG'

            try:
                os.rename(pic,directory+'\\'+new_filename)
            except WindowsError, arg:
                print(os.path.basename(pic),new_filename)
                raise WindowsError, arg
            if args.verbose:
                print ' '*2 + os.path.basename(pic)[:-8] + ' --> ' + new_filename[:-4]
        print '='*40
        print 'Editing Complete!', str(len(jpegs)), 'files modified.'
        print '='*40


modify_jpeg_filename(directory=args.path)
