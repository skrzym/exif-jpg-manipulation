import os
import datetime as dt
import re
import piexif
import argparse
from PIL.ExifTags import TAGS


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
    return (jpeg_files, other_files, sub_dirs)


def logger(msg):
    print msg


def directory_status(directory=os.curdir, log=logger):
    jpegs, others, subdirs = list_dir_jpeg(directory)
    log('=JPEG-FILENAME-MODIFIER-PROGRAM' + '=' * 17)
    log('Ignored files: ' + str(len(others)))
    log('Ignored sub directories: ' + str(len(subdirs)))
    log('JPEG files to be edited: ' + str(len(jpegs)))
    log('=' * 40)
    if len(jpegs) == 0:
        log('There are no "*.JPG" files in supplied directory!')
        log('=' * 40)
    else:
        log('Filename modification program ready...')
        log('Click "Run" to begin.')
        log('=' * 40)


def modify_jpeg_filename(directory=os.curdir, log=logger, verbose=None):
    jpegs, others, subdirs = list_dir_jpeg(directory)
    for pic in jpegs:
            oldpic = pic[:-4]+'_old'+pic[-4:]
            os.rename(pic, oldpic)
    jpegs, others, subdirs = list_dir_jpeg(directory)

    if len(jpegs) != 0:
        log('Editing JPEG Filenames...')

        for pic in jpegs:

            fdt = dt.datetime.strptime(piexif.load(pic)['0th'][306],"%Y:%m:%d %H:%M:%S")

            matches = [
                item
                for item in os.listdir(directory)
                if re.search('IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'(_?[0-9]*)\.[jJ][pP][gG]', item)
            ]
            if len(matches) > 0:
                if os.path.basename(pic) != 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG':
                    new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'_'+str(len(matches))+'.JPG'
            else:
                new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG'

            try:
                os.rename(pic,directory+'\\'+new_filename)
            except OSError, arg:
                log(os.path.basename(pic),new_filename)
                raise OSError, arg
            if verbose:
                log(' '*2 + os.path.basename(pic)[:-8] + ' --> ' + new_filename[:-4])
        log('='*40)
        log('Editing Complete! ' + str(len(jpegs)) + ' files modified.')
        log('='*40)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EXPERIMENTAL! WARNING THIS WILL CHANGE ALL FOUND .JPG FILENAMES! EXPERIMENTAL! This will rename all JPG files in a directory to follow the following capture time format 'IMG_YYYYMMDD_HHMMSS.JPG'. If a conflict arises the script will increment the file name by 1 as such 'IMG_YYYYMMDD_HHMMSS_1.JPG'.")
    parser.add_argument('--path', help="file directory to look for JPG files to modify")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="when set, output shows old and new file names for each modified file")
    args = parser.parse_args()
    modify_jpeg_filename(directory=args.path, verbose=args.verbose)
