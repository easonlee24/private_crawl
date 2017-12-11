# -*- coding: utf-8 -*- 
import os
import shutil

class ChangePdfPath:
    """This mainly use for OA

    we first download all pdf, and then use this script to move pdf to target path

    Args:
        pdf_path_info: this file contain pdf path info,it's format like following
            [target_path],[pdf_link],[doi]

        pdf_save_dir: current pdf dir that save pdf

    """
    def __init__(self, pdf_path_info, old_pdf_save_dir):
        self.pdf_path_info = pdf_path_info

    def start(self):
        with open(self.pdf_path_info) as fp:
            for line in fp:
                pdf_path_infos = line.split(',')

                target_pdf_path = pdf_path_info[0]
                doi = pdf_path_info[2]

                target_pdf_path.replace(" C:\Users\hp\Desktop\xml_result", "F:\crawled_by_chelu\\")
                old_pdf_save_path = old_pdf_save_dir + "/" + doi.replace("/", "_") + ".pdf"

                if (not os.path.exists(old_pdf_save_path)):
                    print "not exist: %s" % line
                    continue

                shutil.copy(old_pdf_save_path, target_pdf_path)
                    


if __name__ == "__main__":
    pdf_path_info = sys.argv[1]
    old_pdf_save_dir = sys.argv[2]

    change_pdf_path = ChangePdfPath(pdf_path_info, old_pdf_save_dir)
    change_pdf_path.start()
