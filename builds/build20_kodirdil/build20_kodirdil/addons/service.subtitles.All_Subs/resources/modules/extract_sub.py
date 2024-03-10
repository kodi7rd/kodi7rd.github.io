
import zipfile
import xbmcvfs
import os,gzip,shutil
from resources.modules import log
exts = [".idx",".sup",".srt", ".sub", ".str", ".ass"]
def convert_to_utf(file):
    import codecs
    try:
        with codecs.open(file, "r", "cp1255") as f:
            srt_data = f.read()

        with codecs.open(file, 'w', 'utf-8') as output:
            output.write(srt_data)
    except: pass
    
def extract(archive_file,MySubFolder):
    try:
        with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(MySubFolder)
                        
        os.remove(archive_file)
        for file_ in xbmcvfs.listdir(MySubFolder)[1]:
            ufile = file_
            file_ = os.path.join(MySubFolder, ufile)
            for items in exts:
                if os.path.splitext(ufile)[1] == items:
                    convert_to_utf(file_)
                    
                    return file_
    except Exception as e:
        log.warning('Error Extract:'+str(e))
        return archive_file
    return '0'
def g_extract(archive_file,dest,MySubFolder):
    log.warning(archive_file)
    with gzip.open(archive_file, 'rb') as f_in:
            with open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    os.remove(archive_file)
    for file_ in xbmcvfs.listdir(MySubFolder)[1]:
        ufile = file_
        file_ = os.path.join(MySubFolder, ufile)
        if os.path.splitext(ufile)[1] in exts:
            convert_to_utf(file_)
            
            return file_