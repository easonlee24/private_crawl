# -*- coding: utf-8 -*- 
import os
import shutil
import sys
import shutil

class ChangePdfPath:
    """This mainly use for OA

    reset wiley filename

    """
    def __init__(self, origin_dir, target_dir):
        self.origin_dir = origin_dir
        self.target_dir = target_dir

    def start(self):
        for dirname in os.listdir(self.origin_dir):
            dirpath = os.path.join(self.origin_dir, dirname)
            if not os.path.isdir(dirpath):
                continue

            for filename in os.listdir(dirpath):
                origin_filepath = os.path.join(dirpath, filename)
                new_filepath = os.path.join(self.target_dir, dirname + ".pdf")
                print "copy file from %s to %s" % (origin_filepath, new_filepath)
                shutil.copyfile(origin_filepath, new_filepath)
        

if __name__ == "__main__":
    origin_dir = sys.argv[1]
    target_dir = sys.argv[2]

    change_pdf_path = ChangePdfPath(origin_dir, target_dir)
    change_pdf_path.start()
