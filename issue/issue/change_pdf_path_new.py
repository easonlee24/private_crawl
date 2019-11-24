# -*- coding: utf-8 -*- 
import os
import shutil
import sys
import xlrd
from spiders.utils import  Utils

class ChangePdfPath:
    """ 用于OA的pdf改名, 20190616更新
    """
    def __init__(self, xls_file, old_dir, new_dir, miss_file_path):
        self.xls_file = xls_file
        self.old_dir = old_dir
        self.new_dir = new_dir
        self.miss_file_writer = open(miss_file_path, "w+")
        self.filename_map = {}
        self.error_count = 0
        self.file_count = 0

    def load_xls(self):
        data = xlrd.open_workbook(self.xls_file)
        table = data.sheets()[0] #3rd sheet is main sheet
        nrows = table.nrows
        ncols = table.ncols
        columns = table.row_values(0)

        doi_index = columns.index("doi")
        filename_index = columns.index("file_name")
        pdf_index = columns.index("download_path")
        filepath_index = columns.index("file_path")
        for i in xrange(1,nrows):
            self.file_count += 1
            rowValues = table.row_values(i)
            doi = rowValues[doi_index]
            pdf_url = rowValues[pdf_index]
            new_filename = rowValues[filename_index]
            filepath = rowValues[filepath_index]
            try:
                if filepath.find("scienceopen")!= -1 and filepath.find("vid=") != -1:
                    #scienceopen是模拟点击的，pdf名称比较特殊
                    elems = filepath.split("=")
                    old_filename = elems[1] + ".pdf"
                else:
                    if doi !=  "":
                        old_filename = Utils.doi_to_filname(doi) + ".pdf"
                    else:
                        old_filename = filename = "_".join(pdf_url.split('/')[-1:]) + ".pdf"
            except Exception as e:
                print "unexpect doi :%s" % doi
                self.error_count += 1
            self.filename_map[new_filename] = {"filename": old_filename, "download_url": pdf_url}

    def start(self):
        self.load_xls()
        non_exist_count = 0
        exist_count = 0
        move_count = 0
        for new_filename, info in self.filename_map.iteritems():
            old_filename = info["filename"]
            download_url = info["download_url"]
            target_pdf_path = self.new_dir + "\\" + new_filename

            if os.path.exists(target_pdf_path):
                print "%s already exist" % target_pdf_path
                exist_count += 1
                continue

            old_pdf_save_path = self.old_dir + "\\" + old_filename

            if not os.path.exists(old_pdf_save_path):
                non_exist_count = non_exist_count + 1
                print "not exist: %s" % (old_pdf_save_path)
                miss_info = "%s|%s" % (target_pdf_path, download_url)
                #miss_info = "%s" % access_url
                self.miss_file_writer.write(miss_info)
                self.miss_file_writer.write("\n")
            else:
                move_count =  move_count + 1
                print "move from %s to %s" % (old_pdf_save_path, target_pdf_path)
                dir = os.path.dirname(target_pdf_path)
                if (not os.path.exists(dir)):
                    os.makedirs(dir)
                if not os.path.exists(target_pdf_path):
                    shutil.copy(old_pdf_save_path, target_pdf_path)

        print "total_count :%d, exist_count :%d, non_exist_count :%d, move_count: %d, error_count: %s" % (self.file_count, exist_count, non_exist_count, move_count, self.error_count)
        self.miss_file_writer.close()

if __name__ == "__main__":
    xls_file = sys.argv[1]
    old_dir = sys.argv[2]
    new_dir = sys.argv[3]
    miss_file_path = sys.argv[4]

    change_pdf_path = ChangePdfPath(xls_file, old_dir, new_dir, miss_file_path)
    change_pdf_path.start()
