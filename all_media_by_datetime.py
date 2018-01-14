import os
import datetime as dt
import re
import piexif
import argparse
from collections import Counter
import struct
from PIL.ExifTags import TAGS


def is_live(file_list, filename):
    """
    Checks file_list for filename containing .jpg and .mov files
    :param file_list: list of all base file names including their extension
    :param filename: string of filename to check for
    :return: bool
    """
    # generate list of all filename extensions that have the provided filename.
    # If the list contains .JPG and .MOV then return True otherwise false

    file_extensions = [f.lower()[f.find('.'):] for f in file_list if f[0:f.find('.')] == filename[0:filename.find('.')]]
    return ('.jpg' in file_extensions) & ('.mov' in file_extensions) & (filename.lower()[filename.find('.'):] in ['.mov','.jpg'])


def is_heic_live(file_list, filename):
    """
    Checks file_list for filename containing .jpg and .mov files
    :param file_list: list of all base file names including their extension
    :param filename: string of filename to check for
    :return: bool
    """
    # generate list of all filename extensions that have the provided filename.
    # If the list contains .HEIC and .MOV  and NO .JPG then return True otherwise false

    file_extensions = [f.lower()[f.find('.'):] for f in file_list if f[0:f.find('.')] == filename[0:filename.find('.')]]
    return ('.heic' in file_extensions) & ('.mov' in file_extensions) & ('.jpg' not in file_extensions)


def list_dir_files(basedir=os.path.curdir):

    live_files = []
    jpeg_files = []
    mov_files = []
    other_files = []
    sub_dirs = []

    all_items = os.listdir(basedir)
    only_files = [f for f in all_items if os.path.isfile(os.path.join(basedir, f))]

    for item in all_items:
        abs_path = os.path.join(basedir,item)
        if os.path.isfile(abs_path):
            if is_live(only_files, item):
                live_files.append(abs_path)
            elif is_heic_live(only_files, item):
                # print item, 'is heic based live photo! BAD!'
                other_files.append(abs_path)
            elif re.search('(\.JPG)', item, re.IGNORECASE):
                jpeg_files.append(abs_path)
            elif re.search('(\.MOV)', item, re.IGNORECASE):
                mov_files.append(abs_path)
            else:
                other_files.append(abs_path)
        else:
            sub_dirs.append(abs_path)
    return live_files, jpeg_files, mov_files, other_files, sub_dirs


def logger(msg):
    print msg


def directory_status(directory=os.curdir, log=logger):
    lives, jpegs, movs, others, subdirs = list_dir_files(directory)
    log('=MEDIA-FILENAME-MODIFIER-PROGRAM' + '=' * 17)
    log('Ignored files: ' + str(len(others)))
    log('Ignored folders: ' + str(len(subdirs)))
    log('=' * 40)
    log('Files to be edited: ' + str(len(jpegs) + len(lives) + len(movs)))
    log('Live Photos: ' + str(len(lives)))
    log('Regular Photos: ' + str(len(jpegs)))
    log('Videos: ' + str(len(movs)))
    log('=' * 40)
    if (len(jpegs) + len(lives) + len(movs)) == 0:
        log('There are no valid media files in supplied directory!')
        log('=' * 40)
    else:
        log('Filename modification program ready...')
        log('Click "Run" to begin.')
        log('=' * 40)


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
        return dt.datetime.utcfromtimestamp(creation_date - EPOCH_ADJUSTER)# + dt.timedelta(days=args.days,hours=args.hours,minutes=args.minutes,seconds=args.seconds)


def modify_media_filenames(directory=os.curdir, log=logger, verbose=None):
    lives, jpegs, movs, others, subdirs = list_dir_files(directory)
    for live in lives:
        oldlive = live[:-4]+'_old'+live[-4:]
        os.rename(live, oldlive)
    for mov in movs:
        oldmov = mov[:-4]+'_old'+mov[-4:]
        os.rename(mov, oldmov)
    for pic in jpegs:
        oldpic = pic[:-4]+'_old'+pic[-4:]
        os.rename(pic, oldpic)
    lives, jpegs, movs, others, subdirs = list_dir_files(directory)

    if len(lives) != 0:
        log('Editing Live Photo Filenames...')

        live_files = lives
        live_pairs = []
        while len(live_files) > 0:
            cur_file = live_files.pop()
            for index, element in enumerate(live_files):
                if os.path.basename(cur_file).lower()[:-4] == os.path.basename(element).lower()[:-4]:
                    if cur_file.lower()[-4:] == '.jpg':
                        live_pairs.append((cur_file, live_files.pop(index)))
                    else:
                        live_pairs.append((live_files.pop(index), cur_file))

        for pic, movie in live_pairs:
            try:
                fdt = dt.datetime.strptime(piexif.load(pic)['0th'][306], "%Y:%m:%d %H:%M:%S")
            except KeyError:
                log('Key Error! ' + os.path.basename(pic) + ' is being skipped!')
                continue
            matches = [
                item
                for item in os.listdir(directory)
                if re.search('IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'(_?[0-9]*)\.[jJ][pP][gG]', item)
            ]
            if len(matches) > 0:
                if os.path.basename(pic) != 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG':
                    new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'_'+str(len(matches))+'.JPG'
                    new_videoname = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'_'+str(len(matches))+'.MOV'
            else:
                new_filename = 'IMG_'+'{:%Y%m%d_%H%M%S}'.format(fdt)+'.JPG'
                new_videoname = 'IMG_' + '{:%Y%m%d_%H%M%S}'.format(fdt) + '.MOV'

            try:
                os.rename(pic, directory + '\\' + new_filename)
            except OSError, arg:
                log(os.path.basename(pic) + new_filename)
                raise OSError, arg

            try:
                os.rename(movie, directory + '\\' + new_videoname)
            except OSError, arg:
                log(os.path.basename(movie) + new_videoname)
                raise OSError, arg

            if verbose:
                log(' '*2 + os.path.basename(pic)[:-8] + ' --> ' + new_filename[:-4])
                log(' ' * 2 + os.path.basename(movie)[:-8] + ' --> ' + new_videoname[:-4])
        log('Live Photos Editing Complete! ' + str(len(lives)) + ' files modified.')
        log('=' * 40)

    if len(jpegs) != 0:
        log('Editing JPEG Filenames...')

        for pic in jpegs:
            try:
                fdt = dt.datetime.strptime(piexif.load(pic)['0th'][306], "%Y:%m:%d %H:%M:%S")
            except KeyError:
                log('Key Error! ' + os.path.basename(pic) + ' is being skipped!')
                continue
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
                log(os.path.basename(pic) + new_filename)
                raise OSError, arg
            if verbose:
                log(' '*2 + os.path.basename(pic)[:-8] + ' --> ' + new_filename[:-4])
        log('JPG Editing Complete! ' + str(len(jpegs)) + ' files modified.')
        log('='*40)

    if len(movs) > 0:
        log('Editing MOV Filenames...')

        for mov in movs:

            # fdt = datetime.datetime.strptime(piexif.load(mov)['0th'][306],"%Y:%m:%d %H:%M:%S")
            fdt = get_mov_datetime(mov)

            matches = [
                item
                for item in os.listdir(directory)
                if re.search('MOV_' + '{:%Y%m%d_%H%M%S}'.format(fdt) + '(_?[0-9]*)\.[mM][oO][vV]', item)
            ]
            if len(matches) > 0:
                if os.path.basename(mov) != 'MOV_' + '{:%Y%m%d_%H%M%S}'.format(fdt) + '.MOV':
                    new_filename = 'MOV_' + '{:%Y%m%d_%H%M%S}'.format(fdt) + '_' + str(len(matches)) + '.MOV'
            else:
                new_filename = 'MOV_' + '{:%Y%m%d_%H%M%S}'.format(fdt) + '.MOV'

            try:
                os.rename(mov, directory + '\\' + new_filename)
            except OSError, arg:
                log(os.path.basename(mov) + new_filename)
                raise OSError, arg
            if verbose:
                log(' ' * 2 + os.path.basename(mov)[:-8] + ' --> ' + new_filename[:-4])
        log('MOV Editing Complete! ' + str(len(movs)) + ' files modified.')
        log('=' * 40)
    log('Conversions completed.')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EXPERIMENTAL! WARNING THIS WILL CHANGE ALL FOUND .JPG FILENAMES! EXPERIMENTAL! This will rename all JPG files in a directory to follow the following capture time format 'IMG_YYYYMMDD_HHMMSS.JPG'. If a conflict arises the script will increment the file name by 1 as such 'IMG_YYYYMMDD_HHMMSS_1.JPG'.")
    parser.add_argument('--path', help="file directory to look for JPG files to modify")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="when set, output shows old and new file names for each modified file")
    args = parser.parse_args()
    modify_media_filenames(directory=args.path, verbose=args.verbose)
