import os
import datetime as dt
import re
import piexif
import argparse
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser(description="Apply a timedelta transformation to the EXIF metadata of a supplied directory's JPEG files. Positive values move time forward in the given increment type. Negative values do the opposite.")
parser.add_argument('--path', help="file directory to look for JPG files to modify")
parser.add_argument('--days', type=int, default=0, help="integer value adjusts datetime 'day' value")
parser.add_argument('--hours', type=int, default=0, help="integer value adjusts datetime 'hour' value")
parser.add_argument('--minutes', type=int, default=0, help="integer value adjusts datetime 'minute' value")
parser.add_argument('--seconds', type=int, default=0, help="integer value adjusts datetime 'second' value")
parser.add_argument("-v", "--verbose", action='store_true',
                    help="when set, output shows old and new datetime values for each modified file")
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

def modify_jpeg_exif_datetimes(filename,td):
    exif_dict = piexif.load(filename)
    for key in exif_dict.keys():
        if type(exif_dict[key]) == dict:
            for item in exif_dict[key].keys():
                tag = TAGS.get(item,item)
                if 'Date' in str(tag):
                    old_date_string = exif_dict[key][item]
                    old_date_dt = dt.datetime.strptime(old_date_string,"%Y:%m:%d %H:%M:%S")
                    ndt = old_date_dt + dt.timedelta(days=td[0],hours=td[1],minutes=td[2],seconds=td[3])
                    new_date_string = '{:%Y:%m:%d %H:%M:%S}'.format(ndt)
                    exif_dict[key][item] = new_date_string
    piexif.insert(piexif.dump(exif_dict),filename)
    return (old_date_string,new_date_string)

def modify_jpeg_dates(directory=os.curdir,days=0,hours=0,minutes=0,seconds=0):
    td = [days,hours,minutes,seconds]
    jpegs,others,subdirs = list_dir_jpeg(directory)
    
    print ''
    print '=JPEG-EXIF-DATETIME-MODIFIER'+ '='*12
    print 'Ignored files:', len(others)
    print 'Ignored sub directories:', len(subdirs)
    print 'JPEG files to be edited:', len(jpegs)
    print '='*40
    if len(jpegs) == 0:
        print 'There are no "*.JPG" files in supplied directory!'
        print '='*40
    else:
        print 'JPEG Metadata to be offset as follows:'
        print 'Days:'+str(td[0])+'|'+'Hours:'+str(td[1])+'|'+'Minutes:'+str(td[2])+'|'+'Seconds:'+str(td[3])
        print '='*40
        print 'Editing JPEG Metadata...'
        for pic in jpegs:
            oldtime,newtime = modify_jpeg_exif_datetimes(pic,td)
            if args.verbose:
                print ' '*2 + os.path.basename(pic) + ' | ' + oldtime + ' --> ' + newtime
        print '='*40
        print 'Editing Complete!', str(len(jpegs)), 'files modified.'
        print '='*40

modify_jpeg_dates(directory=args.path,days=args.days,hours=args.hours,minutes=args.minutes,seconds=args.seconds)