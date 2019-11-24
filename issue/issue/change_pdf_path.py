# -*- coding: utf-8 -*- 
import os
import shutil
import sys

class ChangePdfPath:
    """This mainly use for OA

    we first download all pdf, and then use this script to move pdf to target path

    Args:
        pdf_path_info: this file contain pdf path info,it's format like following
            [pdf_uri],[pdf_link],[doi],[xml_uri],[access_url]

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
                pdf_path_infos = line.split('|')

                pdf_uri = pdf_path_infos[0].strip()
                pdf_download_url = pdf_path_infos[1].strip()
                doi = pdf_path_infos[2].strip()
                xml_uri = pdf_path_infos[3].strip()
                access_url = pdf_path_infos[4].strip()

                xml_uri = xml_uri.replace(":", "_")
                target_pdf_dir = os.path.dirname(xml_uri.replace("xml_result", self.xml_result_dir))
                target_pdf_path = target_pdf_dir + "/" + pdf_uri

                if os.path.exists(target_pdf_path):
                    #print "%s already exist" % target_pdf_path
                    continue

                old_pdf_save_path = self.old_pdf_save_dir + "/" + doi.replace("/", "_") + ".pdf"

                pdf_exist = True
                if (not os.path.exists(old_pdf_save_path)):
                    #doi只取后面的部分
                    #old_pdf_save_path = self.old_pdf_save_dir + "/" + doi.split("/")[1] + ".pdf"
                    old_pdf_save_path = self.old_pdf_save_dir + "/" + "_".join(doi.split("/")[-1:])+ ".pdf"
                    #pensoft的pdf命名方式有点独特
                    #old_pdf_save_path = self.old_pdf_save_dir + "/" + pdf_download_url.split("/")[-4] + ".pdf"
                    if  not os.path.exists(old_pdf_save_path):
                        ##有的时候oa的保存路径就是Files/xxx
                        #old_pdf_save_path = self.old_pdf_save_dir + "/" + pdf_uri
                        #if not os.path.exists(old_pdf_save_path):
                        #    old_pdf_save_path = self.old_pdf_save_dir + "/Files/" + pdf_download_url.split("/")[-1]
                        #    if not old_pdf_save_path.endswith(".pdf"):
                        #        old_pdf_save_path = old_pdf_save_path + ".pdf"
                        #    if not os.path.exists(old_pdf_save_path):
                        #        pdf_exist = False
                        xml_result_dir = self.xml_result_dir.split("\\")
                        #print xml_result_dir
                        xml_result_dir[-2] = xml_result_dir[-2] + "_1"
                        xml_result_dir = "\\".join(xml_result_dir)
                        #old_pdf_save_path = os.path.dirname(xml_uri.replace("xml_result", xml_result_dir))
                        #old_pdf_save_path = old_pdf_save_path + "/" + pdf_uri
                        if not os.path.exists(old_pdf_save_path):
                            pdf_exist = False

                if not pdf_exist:
                    non_exist_count = non_exist_count + 1
                    print "not exist: %s, doi :%s, pdf: %s" % (old_pdf_save_path, doi, pdf_download_url)
                    miss_info = "%s|%s" % (target_pdf_path, pdf_download_url)
                    #miss_info = "%s" % access_url
                    self.miss_file_writer.write(miss_info)
                    self.miss_file_writer.write("\n")
                else:
                    exist_count = exist_count + 1
                    print "move from %s to %s" % (old_pdf_save_path, target_pdf_path)
                    dir = os.path.dirname(target_pdf_path)
                    if (not os.path.exists(dir)):
                        os.makedirs(dir)
                    if not os.path.exists(target_pdf_path):
                        shutil.copy(old_pdf_save_path, target_pdf_path)

        print "exist_count :%d, non_exist_count :%d" % (exist_count, non_exist_count)
        self.miss_file_writer.close()

if __name__ == "__main__":
    pdf_path_info = sys.argv[1]
    old_pdf_save_dir = sys.argv[2]
    xml_result_dir = sys.argv[3]
    miss_pdf_url_file = sys.argv[4]

    change_pdf_path = ChangePdfPath(pdf_path_info, old_pdf_save_dir, xml_result_dir, miss_pdf_url_file)
    change_pdf_path.start()
