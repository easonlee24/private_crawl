# -*- coding: utf-8 -*- 
# Date: 20190528
# Desription: 把oa的元数据转化成excel/access
import os
import sys
import json
import time
import xlrd
import datetime
import re
import urlparse
import xlwt
import linecache
from unidecode import unidecode
from xml.dom import minidom
from spiders.utils import Utils

reload(sys)
sys.setdefaultencoding('utf8')

# set excel cell style
def set_style(name, bold=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name  # 'Times New Roman'
    font.bold = bold
    style.font = font
    return style


def write_excel(dataList, row0, path):
    f = xlwt.Workbook(encoding='utf-8')
    default = set_style('Times New Roman', False)
    sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)
    for i in range(0, len(row0)):
        sheet1.write(0, i, row0[i], default)
    for index in range(0, len(dataList)):
        for i in range(0, len(row0)):
            sheet1.write(index + 1, i, dataList[index][i], default)
    f.save(path)

class Json2OAExcel:
    """Convert metadata result crawled by scrapy to xml
    """
    def __init__(self, all_journal_meta_xls, json_file, save_file, start_article_id = 1, use_new_journal = None, checked_table = None):
        self.json_file = json_file
        self.save_file = save_file
        self.today = time.strftime('%Y%m%d', time.localtime(time.time() - 24*3600))
        self.now = time.strftime('%Y-%m-%dT00:00:00',time.localtime(time.time() - 24 * 3600))
        self.use_new_journal = use_new_journal

        self.all_journal_meta = {}
        #以防某些元数据爬取不到journal name，从excel里面获取journal url与journal name的对应关系
        self.journal_url_to_name = {}
        self.load_journal_meta(all_journal_meta_xls)
        self.journal_ids = {}
        self.next_article_id = int(start_article_id)
        self.current_url = ""


    def convert(self):
        row0 = []
        #首先需要遍历一下所有元数据，获取到元数据中所有出现的列。在转换xls的时候，某列如果不出现在元数据中时，则此列以空字符串填充。
        with open(self.json_file, 'rb') as fp:
            for line in fp:
                line = line.strip()
                try:
                    jsondic = json.loads(line)
                except Exception as e:
                    raise Exception(e)
                    continue

            for k in jsondic:
                if k not in row0:
                    row0.append(k)

            row0.extend(['source_id', 'database_id', 'article_caid', 'article_type', 'file_name', 'institution_id', 'institution', 'full_name', 'process_mode', 'process_level'])

        dataList = []
        with open(self.json_file, 'rb') as fp:
            for line in fp:
                strlen = len(line)
                if strlen > 32672:
                    print "unexcept str len %d:" % strlen
                    continue
                json_data = json.loads(line)
                #添加其他的字段
                journal_name = self.journal_url_to_name[json_data["journal_url"]]
                journal_meta = self.all_journal_meta[journal_name]
                print "journal_url: %s"  % json_data["journal_url"]
                print journal_meta

                json_data['source_id'] = journal_meta["system_id"]
                json_data['database_id'] = journal_meta["source_id"]
                json_data['article_caid'] = self.generate_article_id()
                json_data['article_type'] = "article"
                json_data['file_name'] = "RO%sNK.pdf" % json_data["article_caid"]
                json_data['institution_id'] = "CN111023"
                json_data['institution'] = "NK"
                json_data['full_name'] = "中国农业科学院科技文献信息中心"
                json_data['process_mode'] = "Web_Download"
                json_data['process_level'] = 4

                data = []
                for k in row0:
                    column_data = json_data.get(k, "")
                    if type(column_data) is list:
                        column_data = "".join(filter(None, column_data))
                    data.append(column_data)
                dataList.append(data)
        write_excel(dataList, row0, self.save_file)

    def _get_domain_url(self, url):
      try:
        journal_url = urlparse.urljoin(url, '/').replace("https", "http")
        url = urlparse.urljoin(url, '/').replace("https", "http").replace("www.", "")
        return url
      except Exception:
        return ""

    def load_journal_meta(self, all_journal_meta_xls):
        """
        Load all journal meta info from xls file
        """
        data = xlrd.open_workbook(all_journal_meta_xls)

        #TODO 其他需求journal元数据表可能不是这样
        if not self.use_new_journal:
            table = data.sheets()[2] #3rd sheet is main sheet
        else:
            table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols
        for i in xrange(0,nrows):
            if not self.use_new_journal:
                #TODO 第一行没用，其他需求可能不适用
                if (i < 1):
                    continue

            rowValues= table.row_values(i)

            if not self.use_new_journal:
                journal = unidecode(rowValues[9].lower().strip())
                if journal in self.all_journal_meta:
                   raise Exception("journal find multiple meta info: %s" % journal)

                print "add journal: %s" % journal
                if journal == "":
                    continue
                self.all_journal_meta[journal] = {
                'journal_id': rowValues[0],
                'issn': rowValues[1],
                'eissn': rowValues[2],
                'country': rowValues[5],
                'language': rowValues[6], 
                'system_id': rowValues[40],
                'source_id': rowValues[44]}
                journal_url = rowValues[23]
            else:
                #后面OA新增的期刊，excel格式不一样
                journal = rowValues[4].lower().strip()
                if journal == "":
                    break;
                if journal in self.all_journal_meta:
                   raise Exception("journal find multiple meta info: %s" % journal)

                self.all_journal_meta[journal] = {
                'issn': rowValues[5],
                'eissn': rowValues[6],
                'country': rowValues[9],
                'language': rowValues[7], 'license_type': rowValues[12], 'license_text': '', 'oa_type': rowValues[18], 
                'available_time': rowValues[22],
                'platform_url': rowValues[15], 'source_name': rowValues[14], 'system_id': rowValues[3],
                'collection_id': rowValues[32], 'source_id': rowValues[33]}
                journal_url = self._get_domain_url(rowValues[17])

            self.journal_url_to_name[journal_url] = journal

    def get_journal_id(self, journal_name):
        """
        Generate journal_id, for example:JO201709240000001NK
        """
        if journal_name in self.journal_ids:
            return self.journal_ids[journal_name]

        journal_id = "JO%s%07dNK" % (self.today, self.all_journal_meta[journal_name.lower()]['journal_id'])
        self.journal_ids[journal_name] = journal_id
        return journal_id

    def filter_author_affiliation(self, author_affiliation):
        not_affiliations = ['These authors contributed equally to this work.', 'Author to whom correspondence should be addressed.']

        for not_affiliation in not_affiliations:
            if not_affiliation in author_affiliation.strip():
                return False

        return True

    def format_author_sup(self, author_size, author_sup, supplement = True):
        """
        Filter some invalid author sup, and supplement author sup if need
        For example: author_size is 3, author_sup is ["1,2,", "*"], will return
        ["1,2", "1", "1"]
        """
        if type(author_sup) is not list:
            #may not extract author sup
            author_sup = []

        index = 0
        while(index < len(author_sup)):
            sup_list = author_sup[index].split(',')
            sup_list = [k for k in sup_list if k.isdigit()]
            if len(sup_list) == 0:
                sup_list = ['1']
            author_sup[index] = ",".join(sup_list)
            index = index + 1
        
        if supplement:
            fill_index = len(author_sup)
            while fill_index <= author_size -1:
                author_sup.append('1')
                fill_index = fill_index + 1

        return author_sup

    def generate_article_id(self):
        """
        Generate article id, for example:JA201709240000001NK
        """
        article_id = "%s%07d" % (self.today, self.next_article_id)
        self.next_article_id = self.next_article_id + 1
        return article_id

    def get_article_field(self, article_info, field, convert = True, throw_exception = False):
        fields = field.split("|")
        ret = ""
        for field in fields:
            ret = self.get_article_field_inner(article_info, field, convert, throw_exception)
            if ret != "":
                break
        return ret

    def get_article_field_inner(self, article_info, field, convert = True, throw_exception = True):
        if field not in article_info:
            if throw_exception:
                raise Exception ("field %s is empty, url is :%s" % (field, self.url))
            else:
                ret =  ""
        elif type(article_info[field]) is list:
            if convert:
                ret =  ",".join(filter(None, article_info[field]))
            else:
                ret =  article_info[field]
        else:
            ret = article_info[field]

        try:
            ret = ret.decode('latin1')
        except Exception as e:
            pass

        if ret is None:
            ret = ""
        return ret

if __name__ == "__main__":
    use_new_journal = False
    if len(sys.argv) == 4:
        journal_meta = sys.argv[1]
        input_filename = sys.argv[2]
        save_path = sys.argv[3]
        start_article_id = 1
    elif len(sys.argv) == 5:
        journal_meta = sys.argv[1]
        input_filename = sys.argv[2]
        save_path = sys.argv[3]
        start_article_id = sys.argv[4]
    else:
        print "Usage: python json2xml.py jounal_meta input_filename save_path [start_article_id]"
        sys.exit(1)
        
    json2excel = Json2OAExcel(journal_meta, input_filename, save_path, start_article_id = start_article_id)
    json2excel.convert()
