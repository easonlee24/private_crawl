# -*- coding: utf-8 -*-
import re
import datetime
import time
import uuid
import os
import json
import xlrd
import sys
"""
Provide some utils function to crawl web data
"""
class Utils(object):
    """
    Select element by content, if not find, throw exception

    @param selected_content: 可以用|分隔
    """
    @staticmethod
    def select_element_by_content(response, xpath, selected_content):
        selected_contents = selected_content.split('|')
        for content in selected_contents:
            elem = Utils._select_element_by_content_inner(response, xpath, content)
            if elem is not None:
                return elem

        raise Exception("can not found element(%s) with content(%s)" % (xpath, selected_content))

    """
    First select elements by content, Then join all contents from these selected elements

    @param 可以用来爬取有多重ISBN的场景，比如EPUB、PDF、HTML
    """
    @staticmethod
    def get_all_inner_texts_from_selected_element(response, xpath, selected_content):
        selected_contents = selected_content.split('|')
        rets = []
        for content in selected_contents:
            try:
                selected_elem = Utils.select_element_by_content(response, xpath, content)
            except Exception:
                continue
            rets.append(Utils.get_all_inner_texts(selected_elem, None))

        return ",".join(rets)
        
    """
    获取元素下面的所有文本内容，排除其他内嵌标签的影响。
    xpath里面不需要写"//text()"，其实实现的秘诀就是用//text()而不是/text()
    具体可以参考这篇问答：https://stackoverflow.com/questions/10618016/html-xpath-extracting-text-mixed-in-with-multiple-tags
    """
    @staticmethod
    def get_all_inner_texts(response, xpath, split_char = '\n'):
        if xpath is None:
            elems = [response]
        else:
            elems = response.xpath(xpath)
        content = ""
        for elem in elems:
            # inner text should strip newchar and join with space
            elem_text = " ".join([v.replace("\n", " ") for v in elem.xpath(".//text()").extract()])
            content = content + elem_text + split_char
        content = content.strip()
        content = re.sub('\t+', ' ', content)
        content = re.sub(' +', ' ', content)
        return content


    @staticmethod
    def replcace_not_ascii(origin, replace_char=' '):
        result = re.sub(r'[^\x00-\x7F]+', replace_char, origin)
        result = re.sub(' +', ' ', result)
        return result

    @staticmethod
    def remove_separator(origin):
        return origin.replace("\n", "").replace("\t", "").strip()

    @staticmethod
    def _select_element_by_content_inner(response, xpath, selected_content):
        found = False
        elements = response.xpath(xpath)
        for element in elements:
            elem_text = "".join(element.xpath(".//text()").extract())
            if elem_text and elem_text.lower().find(selected_content.lower()) != -1:
                selected_elemment = element
                found = True
                break

        if not found:
            return None

        return selected_elemment

    """
    字符串转数字，并且可以处理罗马数字
    """
    @staticmethod
    def str_to_num(num_str):
        if num_str.isdigit():
            ret =  int(num_str)
        else:
            #尝试解析罗马数字
            ret =  Utils.transform_roman_num2_alabo(num_str)
        return ret

    """
    将罗马数字转化为阿拉伯数字 
    """
    @staticmethod
    def transform_roman_num2_alabo(one_str):
        one_str = one_str.upper()
        define_dict={'I':1,'V':5,'X':10,'L':50}  
        if one_str=='0':  
            return 0
        else:  
            res=0
            for i in range(0,len(one_str)):
                if one_str[i] not in define_dict:
                    raise Exception("not roman")

                if i==0 or define_dict[one_str[i]]<=define_dict[one_str[i-1]]:
                    res+=define_dict[one_str[i]]
                else:
                    res+=define_dict[one_str[i]]-2*define_dict[one_str[i-1]]
            return res


    """
    Parse date from string
    @origin_date: date string crawled, possible format:
        1: November 1, 2017
        2: 1 November 2017
        3: (5 October, 2017)
        4: (November, 2017)
    @return datetime object
    """
    @staticmethod
    def strptime(origin_date):
        print "origin_date :%s" % origin_date
        origin_date = origin_date.replace(".", "").replace(",", "").replace("(", "").replace(")", "")
        dates = origin_date.split()

        # 只有year
        if len(dates) == 1:
            dates = [1, 'Aug', dates[0]]

        # 没有day
        elif len(dates) == 2:
            dates = [1, dates[0], dates[1]]

        elif len(dates) == 0:
            return ""

        month = dates[1]
        day = dates[0]
        month_dict = {
                'Jan' : 1, 
                'January' : 1,
                'Feb' : 2, 
                'February' : 2,
                'Mar' : 3, 
                'March' :3,
                'Apr' : 4, 
                'April' : 4,
                'May' : 5, 
                'June' : 6, 
                "Jun" : 6,
                'July' : 7, 
                'Jul' : 7,
                'Aug': 8,
                'August' : 8,
                'Sept' : 9, 
                'Sep' : 9, 
                'September' : 9,
                'Oct' : 10, 
                'October' : 10,
                'Nov' : 11, 
                'November' : 11,
                'Dec' : 12,
                'December': 12}

        if month not in month_dict:
            month = dates[0]
            day = dates[1]
            if month not in month_dict:
                raise Exception("month not expected: %s, date: %s" % (month, origin_date))

        month = month_dict[month]
        date_obj = datetime.datetime.strptime("%s-%s-%s" % (dates[2], month, day), "%Y-%m-%d")
        return date_obj

    """
    Convert date format crawl to format data format
    @origin_date: date string crawled, possible format:
        1: November 1, 2017
        2: 1 November 2017
        3: (5 October, 2017)
        4: (November, 2017)
    @return str 2017-11-00
    """
    @staticmethod
    def format_datetime(origin_date):
        date_pattern = re.compile("\d{4}-\d{1,2}-\d{1,2}")
        if date_pattern.match(origin_date):
            return origin_date

        date_obj = Utils.strptime(origin_date)

        try:
            ret = date_obj.strftime("%Y-%m-%d")
        except Exception:
            return ""
        return ret

    @staticmethod
    def get_pdf_filename(json_data):
        """
        get pdf filename from a json meta data
        """
        guoyan_pattern = re.compile(".*docid=(?P<docid>-?\d+)&.*")
        if "doi" not in json_data:
            access_url = json_data["access_url"]
            #国研网没有doi，从access_url里面获取docid
            match = guoyan_pattern.match(access_url)
            if match:
                doi = str(match.group("docid"))
            else:
                raise Exception("connot get doi from json_data, %s" % json_data)
        else:
            doi = Utils.format_value(json_data['doi'])
        return Utils.doi_to_filname(doi)
    
    @staticmethod
    def doi_to_filname(doi):
        doi = doi.replace("http://dx.doi.org/", "")
        doi = doi.replace("https://dx.doi.org/", "")
        doi = doi.replace("http://doi.org/", "")
        doi = doi.replace("https://doi.org/", "")
        doi = doi.replace("/", "_")
        if doi == "":
            raise Exception("Unexception doi: %s" % doi)
        return doi

    @staticmethod
    def current_time():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    @staticmethod
    def current_date():
        return time.strftime('%Y%m%d', time.localtime(time.time()))

    @staticmethod
    def extract_with_xpath(root, xpath_str, default_value = ""):
        try:
            result = root.xpath(xpath_str).extract_first().strip()
        except Exception as e:
            result = default_value

        return result

    @staticmethod
    def extract_text_with_xpath(root, xpath_str, default_value = ""):
        return Utils.extract_with_xpath(root, xpath_str + "/text()", default_value)

    """
    如果某个xpath表达式命中了多个元数，则全部提取出来。
    """
    @staticmethod
    def extract_all_with_xpath(root, xpath_str, default_value = "", join_str = ""):
        try:
            result = join_str.join(root.xpath(xpath_str).extract())
            result = result.strip()
        except Exception as e:
            result = default_value

        return result

    @staticmethod
    def extract_all_text_with_xpath(root, xpath_str, default_value = "", join_str = ""):
        return Utils.extract_all_with_xpath(root, xpath_str + "/text()", default_value, join_str)

    @staticmethod
    def generate_workdir(prefix=""):
        work_dir = str(uuid.uuid1())
        if prefix != "":
            work_dir = prefix + "_" + work_dir

        work_dir = os.path.join("workdir", work_dir)#"workdir\\" + work_dir

        print "generate_workdir: %s" % work_dir

        os.makedirs(work_dir)

        return work_dir

    @staticmethod
    def format_value(value, convert=True, join_char = ','):
        if type(value) is list:
            value = [i for i in value if i is not None]
            if not convert:
                return value

            if len(value) == 0:
                value = ""
            else:
                value = join_char.join(value)

        if value is None:
            value = ""
              
        if isinstance(value, int):
            value = str(value)   
          
        value = value.strip()
        return value

    @staticmethod
    def is_json_string(str):
        try:
            json_data = json.loads(str)
        except Exception:
            return False
        return True

    @staticmethod
    def extract_chars(origin, start_chars, end_chars):
        try:
            start_index = origin.index(start_chars) + len(start_chars)
            end_index = origin.index(end_chars)
        except Exception as e:
            print "origin is: %s" % origin
            print "start_chars: %s" % start_chars
            return ""
        return origin[start_index:end_index]

    @staticmethod
    def format_authors_from_json(json_data):
        """
        @param json_data
        """
        author = json_data.get("author")
        author_affiliation = json_data.get("author_affiliation", None)
        if author_affiliation is None:
            author_affiliation = ["unkown"] * len(author)

        if "author_sup" in json_data:
            author_sup = json_data["author_sup"]
            author_sup = Utils._format_author_sup(len(author), author_sup)
        else:
            #如果没有author_sup这个字段，说明作者作何机构是一一对应的,生成一个假的author_sup
            #已知有以下几种情况：
            #a:author_affiliation数目不为1，此时，author 和 author_affiliation的size应该一样
            #b:author_affiliation数目为1，那么所有的作者都属于这个机构
            author_sup = range(1, len(author) + 1)
            if len(author) != len(author_affiliation):
                if len(author_affiliation) == 1:
                    author_sup = [0] * len(author)
                else:
                    print("url %s, size of author(%d) and author_affiliation(%d) should be equal when author_sup not set!"\
                        % (self.url, len(author), len(author_affiliation)))
                    return

        if len(author) != len(author_sup):
            raise Exception("author and authos_sup len not equal, This not gonna happen: %s" % url)
            return
        
        return Utils.format_authors(json_data, author, author_sup, author_affiliation)
        
    @staticmethod
    def parse_generator_str(origin_str):
        """
        convert string with generator pattern to list of string, only support on pattern
        For example: www.baidu.com/page[1-3]
        Return: [
            www.baidu.com/page1, www.baidu.com/page2,www.baidu.com/page3
        ]
        """
        pattern = re.compile("(?P<prefix>.*)\[(?P<startid>\d+)-(?P<endid>\d+)\](?P<suffix>.*)")
        match = pattern.match(origin_str)
        ret = []
        if match:
            prefix = match.group("prefix")
            startid = match.group("startid")
            endid = match.group("endid")
            suffix = match.group("suffix")
            for i in range(int(startid), int(endid) + 1):
                ret.append("%s%s%s" % (prefix, i, suffix))
            return ret

        return [origin_str]
            
    @staticmethod
    def _format_author_sup(author_size, author_sup, supplement = True):
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

    @staticmethod
    def format_authors(json_data, authors, author_sups, author_affiliation):
        """
        @param author_sups 目前不支持一个作者多个机构
        """
        if len(authors) != len(author_sups):
            raise Exception("len of authors(%d), author_sups(%d) not equal" %
                (len(authors), len(author_sups)))

        author_text = "|".join(authors)
        author_affliication_text = ""
        for sup in author_sups:
            try:
                affliication = author_affiliation[int(sup) - 1]
            except Exception as e:
                #还有可能作者引用的机构不存在的情况,比如：
                #https://www.intechopen.com/books/advances-in-solid-state-lasers-development-and-applications/laser-driven-proton-acceleration-research-and-development
                print "get afflication error: %s" % json_data["access_url"]
                affliication = "unkown"
            affliication = re.sub('\[\d+\]', '', affliication)
            author_affliication_text += affliication + "|"

        author_affliication_text = author_affliication_text.strip("|")
        json_data['author'] = author_text
        json_data['author_affiliation'] = author_affliication_text
        return json_data

    @staticmethod
    def regex_extract(text, regex_str):
        regexp = re.compile(regex_str)
        match = regexp.search(text)
        if not match:
            return ""

        return "".join([g for g in match.groups() or match.group() if g])

    @staticmethod
    def format_text(text):
        ret = text.replace("\n", "")
        return ' '.join(ret.split())

    """
    OA期刊判断sup是否是有效的
    """
    @staticmethod
    def is_valiad_author_sup(sup):
        return sup.isdigit() or sup == "*"

    @staticmethod
    def is_valiad_affliation_sup(sup):
        return sup.isdigit()

    @staticmethod
    def is_valid_affliation(affiliation, origin_blacklist = None):
        affiliation = affiliation.replace("\n", "").strip()
        blacklist = ["Corresponding Author", "Email"]
        blacklist.extend(origin_blacklist)
        if affiliation == "":
            return False;

        for i in blacklist:
            if affiliation.find(i) != -1:
                return False;

        return True;

    @staticmethod
    def format_oa_sup(sup):
        if sup == "":
            return ""
        sups = sup.split(",")
        sups = [v for v in sups if Utils.is_valiad_author_sup(v)]
        return ",".join(sups)

    def load_journal_meta(all_journal_meta_xls):
        """
        Load all journal meta info from xls file

        Return List
        """
        all_journal_meta = {}
        data = xlrd.open_workbook(all_journal_meta_xls)

        #TODO 其他需求journal元数据表可能不是这样
        table = data.sheets()[2] #3rd sheet is main sheet
        nrows = table.nrows
        ncols = table.ncols
        for i in xrange(0,nrows):
            #TODO 前两行没用，其他需求可能不适用
            if (i <= 1):
                continue

            rowValues= table.row_values(i)

            journal = rowValues[9].lower().strip()
            if journal in all_journal_meta:
               raise Exception("journal find multiple meta info: %s" % journal)

            all_journal_meta[journal] = {
            'journal_id': rowValues[0],
            'issn': rowValues[1],
            'eissn': rowValues[2],
            'country': rowValues[5],
            'language': rowValues[6],
            'license_type': rowValues[17],
            'license_text': rowValues[18],
            'oa_type': rowValues[19], 
            'available_time': rowValues[20],
            'journal_url': rowValues[23],
            'platform_url': rowValues[27],
            'system_id': rowValues[40],
            'collection_id': rowValues[43],
            'source_id': rowValues[44]}
        return all_journal_meta



if __name__ == '__main__':
    #text = "Vol. 35, No. 1 (April 2010), pp. 51-71"
    #print Utils.regex_extract(text, "Vol. (\d+), No. (\d+)")
    str = "www.baidu.com/page[1-3]"
    print Utils.parse_generator_str(str)
