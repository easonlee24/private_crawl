# -*- coding: utf-8 -*- 
import os
import shutil
import sys

class ChangePdfPath:
    """This mainly use for OA

    we first download all pdf, and then use this script to move pdf to target path

    Args:
        pdf_path_info: this file contain pdf path info,it's format like following
            [pdf_uri],[pdf_access_url],[doi],[xml_uri]

        pdf_save_dir: current pdf dir that save pdf

    """
    def __init__(self, pdf_path_info, old_pdf_save_dir, xml_result_dir, miss_pdf_url_file):
        self.pdf_path_info = pdf_path_info
        self.old_pdf_save_dir = old_pdf_save_dir
        self.xml_result_dir = xml_result_dir
        self.miss_file_writer = open(miss_pdf_url_file, "w")

    def start(self):
        non_exist_count = 0
        exist_count = 0
        with open(self.pdf_path_info) as fp:
            for line in fp:
                line =  line.strip()
                pdf_path_infos = line.split(',')

                pdf_uri = pdf_path_infos[0]
                pdf_download_url = pdf_path_infos[1]
                doi = pdf_path_infos[2]
                xml_uri = pdf_path_infos[3]

                print "doi :%s" % doi

                target_pdf_dir = os.path.dirname(xml_uri.replace("./xml_result", self.xml_result_dir))
                target_pdf_path = target_pdf_dir + "/" + pdf_uri

                old_pdf_save_path = self.old_pdf_save_dir + "/" + doi.replace("/", "_") + ".pdf"

                if (not os.path.exists(old_pdf_save_path)):
                    non_exist_count = non_exist_count + 1
                    print "not exist: %s" % old_pdf_save_path
                    miss_info = "%s|%s" % (target_pdf_path, pdf_download_url)
                    self.miss_file_writer.write(miss_info)
                    self.miss_file_writer.write("\n")
                else:
                    exist_count = exist_count + 1
                    print "move from %s to %s" % (old_pdf_save_path, target_pdf_path)
                    dir = os.path.dirname(target_pdf_path)
                    if (not os.path.exists(dir)):
                        os.makedirs(dir)
                    #shutil.copy(old_pdf_save_path, target_pdf_path)

        print "exist_count :%d, non_exist_count :%d" % (exist_count, non_exist_count)
        self.miss_file_writer.close()

if __name__ == "__main__":
    pdf_path_info = sys.argv[1]
    old_pdf_save_dir = sys.argv[2]
    xml_result_dir = sys.argv[3]
    miss_pdf_url_file = sys.argv[4]

    change_pdf_path = ChangePdfPath(pdf_path_info, old_pdf_save_dir, xml_result_dir, miss_pdf_url_file)
    change_pdf_path.start()
