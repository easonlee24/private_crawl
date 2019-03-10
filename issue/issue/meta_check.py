#!/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import re
from datetime import datetime
from spiders.utils import Utils
import argparse
import os
from w3lib.html import remove_tags

"""
Meta检查，同时对key做一些归一化的操作
如果指定了pdf的保存目录，还会自动与pdf文件做join
"""
class MetaCheck(object):
    def __init__(self, args):
        self.args = args

        self.meta_file = args.file
        self.pass_meta_file = args.pass_meta_file
        self.bad_meta_file = args.bad_meta_file
        self.miss_pdf_file = args.miss_pdf_file
        self.for_oa = args.for_oa.lower() == "true"

        self.no_access_url = 0
        self.json_fail = 0
        self.incomplete = 0
        self.total = 0
        self.pass_count = 0
        self.dup = 0
        self.pdf_exist = 0
        self.pdf_non_exist = 0

        self.reserved_non_converted_keys = [
            "author_affiliation",
            "author_sup",
            "author",
            #"keywords"
        ]

        self.required_keys = [
            "title",
            "release_date",
            "doi",
            #"abstracts",
            #sage的 issue和pages有些确实为空。。。
            #"issue",
            #"pages"
            ]
  
        self.pass_meta_map = {} # used to uniq
        
        #把一些不规则的key, 都归一化为统一的key
        self.key_map = {
            "url" : "access_url",
            "pdf_download" : "pdf_url",
            "date" : "release_date",
            "publish_date" : "release_date",
            "publish_year" : "release_year",
            "author_afflication" : "author_affiliation",
            "author_affiliations" : "author_affiliation",
            "author_affliation" : "author_affiliation",
            "volumn": "volume",
            "author_raw" : "author",
            "author_affiliation_raw" : "author_affiliation",
            "DOI" : "doi"
        }

        self._init()

    def __del__(self):
        self.pass_meta_writer.close()
        self.bad_meta_writer.close()
        self.miss_pdf_writer.close()

    def _init(self):
        #reverse_key_map记录了，那些规则的key,可能有哪些不规则的表达
        self.reverse_key_map = {}
        for k, v in self.key_map.items():
            if v in self.reverse_key_map:
                self.reverse_key_map[v].append(k)
            else:
                self.reverse_key_map[v] = [k]
        
        #创建一个workdir
        workdir = Utils.generate_workdir()
        self.pass_meta_file = os.path.join(workdir, self.pass_meta_file)#workdir + "\\" + self.pass_meta_file
        self.bad_meta_file = os.path.join(workdir, self.bad_meta_file)#workdir + "\\" + self.bad_meta_file
        self.miss_pdf_file = os.path.join(workdir, self.miss_pdf_file)#workdir + "\\" + self.miss_pdf_file
        self.pass_meta_writer = open(self.pass_meta_file, "w")
        self.bad_meta_writer = open(self.bad_meta_file, "w")
        self.miss_pdf_writer = open(self.miss_pdf_file, "w")

    def _transform(self, json_data):
        access_url = self._get_value(json_data, "access_url")

        if access_url.find("intechopen.com") != -1:
            json_data =  self._transform_intechopen(json_data)
        elif access_url.find("wiley.com") != -1:
            json_data =  self._transform_wiley(json_data)
        elif access_url.find("scielo") != -1:
            json_data =  self._transform_scielo(json_data)
        elif access_url.find("sagepub") != -1:
            json_data = self._transform_sage(json_data)
        elif access_url.find("pensoft") != -1:
            json_data = self._transform_pensoft(json_data)

        return json_data

    def _transform_sage(self, json_data):
        #用portia爬取的sage，少了doi
        doi = self._get_value(json_data, "doi")
        if doi == "":
            doi = Utils.regex_extract(self._get_value(json_data, "access_url"), ".*sagepub.com/doi/full/(.*)")
            json_data["doi"] = doi
        return json_data
        
    def _transform_pensoft(self, json_data):
        #用portia爬取的sage，少了doi
        json_data["page"] = "%s-%s" % (json_data["fpage"], json_data["lpage"])
        author_elems = json_data["authors"].split(";")
        authors = []
        author_affliications = []
        author_sups = []
        index = 1
        for author_elem in author_elems:
            elems = author_elem.split("@@")
            if len(elems) != 2:
                continue
            authors.append(elems[0])
            author_affliications.append(elems[1])
            author_sups.append(str(index))
            index = index + 1
        json_data["author"] = authors
        json_data["author_affliication"] = author_affliications
        json_data["author_sub"] = author_sups
        return json_data

    def _transform_scielo(self, json_data):
        if type(json_data["date"]) is list:
            tmp = " ".join(json_data["date"])
        else:
            tmp = json_data["date"]
        dates = tmp.encode("utf-8").replace("\xa0", " ").replace("\xc2", " ").replace(".", "").split()

        if len(dates) == 1:
            date = dates[0]
        else:
            try:
                date = Utils.format_datetime(" ".join(dates[-2:]))
            except Exception:
                try:
                    date = Utils.format_datetime(" ".join(dates[-3:]))
                except Exception:
                    date = "%s-08-01" % dates[-1]

        json_data["release_date"] = date
        return json_data

    def _transform_wiley(self, json_data):
        doi = self._get_value(json_data, "doi")
        if doi == "":
            doi = Utils.regex_extract(self._get_value(json_data, "access_url"), ".*onlinelibrary.wiley.com/doi/(.*)")
            json_data["doi"] = doi
        return json_data

    def _transform_intechopen(self, json_data):
        item_type = self._get_value(json_data, "_type")
        if item_type == "book_item":
            #book主要是从content里面抽取一些字段出来
            content = self._get_value(json_data, "content")
            #Edited by Aldemaro Romero and Edward O. Keith , ISBN 978-953-51-0844-3, 248 pages, Publisher: InTech, Chapters published November 07, 2012 under CC BY 3.0 license DOI: 10.5772/2731 Edited Volume
            #Authored by Amira Abdelrasoul, Huu Doan and Ali Lohi , ISBN 978-953-51-3662-0, Print ISBN 978-953-51-3661-3, 232 pages, Publisher: InTech, Chapters published December 06, 2017 under CC BY-NC 4.0 license DOI: 10.5772/65691 Monograph
            #ISBN 978-953-51-3376-6, Print ISBN 978-953-51-3375-9, 262 pages, Publisher: InTech, Chapters published August 23, 2017 under CC BY 3.0 license DOI: 10.5772/intechopen.68449 Monograph
            content_regex = re.compile("(?P<authors>(Edited|Authored) by .*, )?ISBN (?P<isbn>[\w-]+), (?P<print_isbn>Print ISBN .*, )?(?P<pages>\d+) pages, Publisher: (?P<publisher>.*), Chapters published (?P<publish_date>.*) under (?P<license_type>.* license).*")
            match = content_regex.match(content)
            if not match:
                print json_data
                raise Exception("content not match regex: %s" % content)

            json_data['dc:creater'] = match.group("authors")
            json_data['eisbn'] = match.group("isbn")
            json_data['hardcover_PISBN'] = match.group("print_isbn")
            json_data['page'] = match.group("pages")
            json_data['publisher'] = match.group("publisher")
            json_data['release_date'] = Utils.strptime(match.group("publish_date")).strftime("%Y-%m-%d")
            json_data['license_type'] = match.group("license_type")

            json_data.pop('chapters', None)
            json_data.pop('content', None)

        elif item_type == "chapter_item":
            #chapter主要是抽取处理一下作者机构
            if self._key_exist(json_data, "author_affliication"):
                #表示
                author = self._get_value(json_data, "author")
                start_chars = "<div class=\"authors-front\">"
                end_chars = "</div>"
                author_content = Utils.extract_chars(author, start_chars, end_chars)
                if author_content == "":
                    #还有获取不到作者的情况..
                    author_content = self._get_value(json_data, "author_field")

                #有的作者可能有多个sup的情况,比如<sup>1, </sup><sup>2</sup>,需要归一化
                author_content = re.sub("<sup>(\d*)(, ){0,1}</sup>", "<sup>\g<1></sup>", author_content)
                #有的作者还是以and分隔的
                author_content.replace("and", ",")
                author_elems = author_content.split(",")

                authors = []
                author_sups = []
                author_affliication = json_data['author_affliication']
                author_affliication = [x for x in author_affliication if \
                    x.strip().startswith('[')]
                for author_elem in author_elems:
                    sup_start_chars = "<sup>"
                    sup_end_chars = "</sup>"
                    try:
                        sup_start_index = author_elem.index(sup_start_chars)
                        author_text = author_elem[0:sup_start_index]
                        sup = Utils.extract_chars(author_elem, sup_start_chars, sup_end_chars)
                    except Exception as e:
                        sup = "1"
                        author_text = author_elem

                    if not sup.isdigit():
                        sup = "1"

                    authors.append(author_text)
                    author_sups.append(sup)

                json_data = Utils.format_authors(json_data, authors, author_sups, author_affliication)
                json_data.pop('author_field', None)
                   
        return json_data
        
    def start(self):
        #a = "<font size=\"5\"><a name=\"top1\"></a>Efeito de fungicidas na    germinação <i>in vitro</i> de conídios de <i>Claviceps    africana</i><sup>(<a href=\"#back1\">1</a>)</sup></font>"
        #self._format_scielo_authors(a)
        #sys.exit(0)
        with open(self.meta_file) as f:
            for line in f:
                try:
                    self.total = self.total + 1
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    self.json_fail = self.json_fail + 1
                    continue

                #检查1:access url是最基本的字段了，如果这个都没爬取下来，那连问题都没法定位了
                access_url = self._get_value(json_data, "access_url")
                if access_url == "":
                    self.no_access_url = self.no_access_url + 1
                    continue

                #针对不同的平台，对元数据做一些特殊处理
                json_data = self._transform(json_data)

                
                #检查2:检查是否采集必备字段
                miss_required_filed = False
                for key in self.required_keys:                
                    value = self._get_value(json_data, key)
                    if value == "":
                        #value为空，表示元数据未采集到此字段
                        bad_record = {}
                        bad_record['reason'] = "%s empty" % key
                        bad_record['access_url'] = access_url
                        self._mark_bad_record(bad_record)
                        self.incomplete = self.incomplete + 1
                        miss_required_filed = True
                        break

                if miss_required_filed:
                    continue
                
                #检查3:检查元数据里面是否有非空字段
                fail = False
                for key, value in json_data.iteritems():
                    key = key.strip(":").strip()
                    value = Utils.format_value(value)
                    if value == "" and key in self.required_keys:
                        if key == "release_year":
                            publish_data = self._get_value(json_data, "release_date")
                            if publish_data != "":
                                #if publish data is also empty, there is no way to get publish_year
                                json_data["release_year"] = publish_data.split("-")[0]
                                print "publish year is %s" % json_data["release_year"]
                                continue

                        bad_record = {}
                        bad_record['reason'] = "%s empty" % key
                        bad_record['access_url'] = access_url
                        self._mark_bad_record(bad_record)
                        self.incomplete = self.incomplete + 1
                        fail = True
                        break

                if fail:
                    continue

                #检查4:补充一些必备字段
                json_data['acquisition_time'] = Utils.current_time()
                publish_year = self._get_value(json_data, "release_year")
                if publish_year == "":
                    publish_data = self._get_value(json_data, "release_date")
                    if publish_data != "":
                        json_data["release_year"] = publish_data.split("-")[0] 

                #处理一下author、author_sub、author_affiliation等字段        

                if access_url in self.pass_meta_map:
                    title = self._get_value(json_data, "title")
                    if title != self.pass_meta_map[access_url]:
                        pass
                        #raise Exception("same url with different title, not gonna happen :%s" % access_url)
                    self.dup = self.dup + 1
                    continue

                self.pass_count = self.pass_count + 1
                self._mark_success_record(json_data)
                self.pass_meta_map[access_url] = json_data["title"]

        if self.args.pdf_dir is not None:
            print "total: %d, no_access_url: %d, json_fail: %d, incomplete: %d, dup_count: %d, pass_count: %d. pdf_non_exist: %d, pdf_exist_count: %d, pass meta save to: %s, fail meta save to :%s, miss pdf url save to :%s" \
            % (self.total, self.no_access_url, self.json_fail, self.incomplete, self.dup, self.pass_count, self.pdf_non_exist, self.pdf_exist, self.pass_meta_file, self.bad_meta_file, self.miss_pdf_file)
        else:
            print "total: %d, no_access_url: %d, json_fail: %d, incomplete: %d, dup_count: %d, pass_count: %d. pass meta save to: %s, fail meta save to :%s" \
            % (self.total, self.no_access_url, self.json_fail, self.incomplete, self.dup, self.pass_count, self.pass_meta_file, self.bad_meta_file)

    def check_miss_journal(self):
        """
        check miss journal, args:
        python meta_check.py --file xxx --journal_file xxx(xls file) [--source_name wiley] 
        """
        required_args = ['file', 'journal_file']
        help_message = "python meta_check.py --file xxx --journal_file xxx(xls_file)" \
        "[--source_name xxx(f.e: wiley)]"
        self._verify_args(required_args, help_message)
        all_journal_meta = Utils.load_journal_meta(self.args.journal_file)
        should_crawl_journal_meta = {}
        if self.args.source_name is not None:
            for journal, meta in all_journal_meta.iteritems():
                journal_url = meta['journal_url'].lower()
                source_name = self.args.source_name.lower()
                if journal_url.find(source_name) == -1:
                    continue
                else:
                    should_crawl_journal_meta[journal] = meta
        else:
            should_crawl_journal_meta = all_journal_meta

        crawled_journal = {} 
        with open(self.args.file) as fp:
            for line in fp:
                try:
                    json_data = json.loads(line)
                except Exception as e:
                    continue
                journal = json_data['journal'].lower()
                if journal in crawled_journal:
                    crawled_journal[journal] = crawled_journal[journal] + 1
                else:
                    crawled_journal[journal] = 1

        
        for journal, meta in should_crawl_journal_meta.iteritems():
            if journal not in crawled_journal:
               print "miss %s, url: %s" % (journal, "%s/issues" % meta['journal_url'])

    def check_miss_url(self):
        """
        check miss url
        """
        required_args = ['file', 'url_file']
        help_message = "python meta_check.py --file xxx --url_file xxx(should crawl url file)"
        self._verify_args(required_args, help_message)
        download_urls = []
        with open(self.args.file) as f:
            for line in f:
                line = line.strip()
                json_data = json.loads(line)

                url = self._get_value(json_data, "access_url")
                download_urls.append(url)

        #print download_urls
        with open(self.args.url_file) as f: 
            for line in f:
                line = line.strip()
                if line not in download_urls:
                    print "%s" % line

    def _verify_args(self, required_args, help_message):
        for arg in required_args:
            if not hasattr(self.args, arg):
                raise Exception("%s need to be set, usage: %s" % (arg, help_message))

    def _check_key_exist(self, json_data, key):
        """
        这里的key应该是规则的key
        """
        if key in json_data:
            return True
        
        if key in self.reverse_key_map:
            for alias_key in self.reverse_key_map[key]:
                if alias_key in json_data:
                    return True
        
        return False

    def _get_value(self, json_data, key, default = "", convert = True):
        """
        这里的key应该是规则的key
        """
        value = default
        if key in json_data:
            value = json_data[key]
        elif key in self.reverse_key_map:
            for alias_key in self.reverse_key_map[key]:
                if alias_key in json_data:
                    value =  json_data[alias_key]
                    match_key = alias_key
                    break
        
        ret = Utils.format_value(value, convert)

        #余下，可以针对特定key的value，做一些归一化处理
        if key == "release_date":
            if type(ret) is not list:
                ret = ret.replace("00:00:00", "")
                ret = Utils.format_datetime(ret)
            else:
                if len(ret) == 0:
                    return ""
                ret[0] = ret[0].replace("00:00:00", "")
                ret[0] = Utils.format_datetime(ret[0])
        return ret

    def _key_exist(self, json_data, key):
        return (key in json_data) and (json_data[key] is not None) \
            and (json_data[key] != "")

    def _mark_success_record(self, json_data):
        """
        Mark an success record.

        1. 对Key做一些归一化的工作，同时也可以加一些必备的字段
        2. 如果指定了pdf save dir，则会和pdf文件做拼接
        3. 去掉一些无用的key(比如portia爬取，会加上_template这样的字段)
        @param json_data
        """
        publish_data = self._get_value(json_data, "release_date")
        if "release_year" not in json_data or json_data["release_year"] == "":
            #if publish data is also empty, there is no way to get publish_year
            if "release_date" in json_data:
                json_data["release_year"] = publish_data.split()[-1]

        if "keywords" in json_data:
          if type(json_data["keywords"]) is list \
          and len(json_data["keywords"]) == 1:
            #portia有的期刊爬取keywords，都写到一个元素里面了，应该拆开
            keywords = json_data["keywords"][0].replace("Keywords", "").strip()
            json_data["keywords"] = keywords.split(";")
            if len(json_data["keywords"]) == 1:
              json_data["keywords"] = keywords.split(",")
          elif self.for_oa and type(json_data["keywords"]) is not list:
            keywords = json_data["keywords"].replace("Index terms:", "").replace("Keywords", "").split(";")
            json_data["keywords"] = keywords
            
            #如果是oa，且keywords不是list，要转化为list

        convert_data = {}
        for key, value in json_data.iteritems():
            format_key = key.strip(":").strip().lower()

            if format_key in self.key_map:
                format_key = self.key_map[format_key]

            #这类key，不会把list转换为string
            if format_key in self.reserved_non_converted_keys:
                convert = False
            else:
                convert = not self.for_oa

            value = self._get_value(json_data, format_key, convert = convert) #这里使用_get_value,会对value做一些归一化
            convert_data[format_key] = value

        # 归一化作者和作者机构
        is_scielo = False
        if is_scielo:
            #2018.04.18 崩溃了，scielo的作者单独处理
            if convert_data["author"][0].find("<") != -1:
                author_raw_text = " ".join(convert_data["author"])
                authors = self._format_scielo_authors(author_raw_text)
                convert_data['author'] = authors

            convert_data.pop("author_affiliation", None)
        elif 'author' in convert_data and len(convert_data["author"]) == 1:#这种author可能是一坨html，包含了多个作者并且每个作者的sup也标记在<sup>里面
            #这种情况属于作者机构不太好爬，直接把html文档都爬取到author字段了
            authors, author_sups = self._format_authors(convert_data)
            if 'author_sup' not in convert_data:
                convert_data['author_sup'] = author_sups
            else:
                convert_data['author_sup'] = [self._format_author_sup(sup) for sup in convert_data['author_sup']]
            if len(authors) == 1:
              #如果此时author还是只有一个元素，那么author可能是,分隔的
              authors = authors[0].split(",")

            convert_data['author'] = authors

        if 'author_sup' in convert_data:
            convert_data['author_sup'] = [self._format_author_sup(sup) for sup in convert_data['author_sup']]

        if "author_affiliation" in convert_data and len(convert_data['author_affiliation']) == 1:
            #这种author_affiliation可能是一坨html
            author_affiliation = convert_data['author_affiliation'][0]
            try:
                authors = convert_data['author']
                if author_affiliation.startswith(authors[0]):
                  #这种作者机构是以作者分隔的,比如:https://koedoe.co.za/index.php/koedoe/article/view/188
                  author_affiliation = self._format_author_affiliations_by_author(author_affiliation, authors)
                else:
                  author_affiliation = self._format_author_affiliations(convert_data)
                convert_data['author_affiliation'] = author_affiliation
            except Exception as e:
                #没爬到作者，却爬到了作者机构，先忽略这种情况吧
                authors = []
                convert_data['author_affiliation'] = []
                convert_data['author'] = []
                convert_data['author_sup'] = []

        #有的author_sup里面，会有空字符串，比如scielo
        if "author_sup" in convert_data and type(convert_data["author_sup"]) is list:
            convert_data["author_sup"] = [i for i in convert_data["author_sup"] if i != '']

        if self.args.pdf_dir is not None:
            filename = Utils.get_pdf_filename(json_data)
            pdf_path = os.path.join(self.args.pdf_dir, filename + ".pdf")  
            txt_path = os.path.join(self.args.pdf_dir, filename + ".txt")
            if os.path.exists(pdf_path):
                convert_data["pdf_path"] = filename + ".pdf"
                self.pdf_exist = self.pdf_exist + 1
            elif os.path.exists(txt_path):
                convert_data["pdf_path"] = filename + ".txt"
                self.pdf_exist = self.pdf_exist + 1
            else:
                #print "pdf path(%s) or txt path(%s) not exist" % (pdf_path, txt_path)
                convert_data["pdf_path"] = "wrong"
                self.pdf_non_exist = self.pdf_non_exist + 1
                pdf_link = self._get_value(json_data, "pdf_url")
                if pdf_link == "":
                    raise Exception("cannot get pdf_url from json %s" % json_data)
                self.miss_pdf_writer.write(pdf_link)
                self.miss_pdf_writer.write("\n")

        #归一化author,author_affiliation
        if not self.for_oa:
            pass
            #convert_data = Utils.format_authors_from_json(convert_data)

        #去掉一些key
        if not self.for_oa:
            convert_data.pop("author_sup", None)
        else:
            #oa的需要特别处理下
            convert_data["doi"] = self._get_value(convert_data, "doi").replace("https://doi.org/", "").replace("http://doi.org/", "")
        convert_data.pop('_template', None)

        convert_data_str = json.dumps(convert_data)
        self.pass_meta_writer.write(convert_data_str)
        self.pass_meta_writer.write("\n")

    """
    所有作者可能被写到一个字段
    """
    def _get_author_split_char(self, convert_data):
        return "|"


    def _format_scielo_authors(self, author_raw_text):
        authors = []
        author_index = 0
        sup_start = sup_end = author_index
        while author_index < len(author_raw_text) - 1 and sup_start!= -1 and sup_end != -1:
            sup_start = author_raw_text.find("<sup>", sup_start + 1)
            sup_end = author_raw_text.find("</sup>", sup_start + 1)
            print "author_index: %d, sup_start: %d, sup_end : %d" % (author_index, sup_start, sup_end)
            if sup_start == -1 or sup_end == -1:
                break
            is_sup_value_int = True
            try:
                sup_value = remove_tags(author_raw_text[sup_start + len("<sup>"): sup_end]).strip()
                sup_value = re.sub('[()]', '', sup_value)
                roma_number = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
                print "raw sup_vaule :%s" % sup_value
                if sup_value not in roma_number:
                    sup_value = int(sup_value)
                    print "sup_vaule is int :%d" % sup_value
                else:
                    print "sup_vaule is int :%s" % sup_value
            except Exception as e:
                print "sup_value is not int: %s" % sup_value
                is_sup_value_int = False

            if is_sup_value_int:
                #找到了一个新的作者
                author_text = author_raw_text[author_index: sup_start].strip(';').strip()
                author_text = remove_tags(author_text).strip()
                author_text = re.sub('[(),]', ' ', author_text)
                author_text = re.sub(' +', ' ', author_text)
                authors.append(author_text)
                author_index = sup_end + len("</sup>")
                sup_start = sup_end = author_index

            #否则找到的这个<sup>对并不是<sup>1</sup>这种
        print "author_raw_text :%s" % author_raw_text.encode("utf-8")
        print "return author:"
        print authors
        #sys.exit(0)
        return authors

    """
    for example:
        input:
            authors: ["li zhen <sup>a-c</sup><sup>d</sup>", "chen lu <sup>1-2</sup><sup>3</sup>"]
        return:
            authors: ["li zhen", "chen lu"],
            author_sups: ["1,2,3,4", "1,2,3"]
    """
    def _format_authors(self, article_info):
        author = article_info["author"][0]
        author = re.sub(r'\xb7', r'|', author) #十六进制字符，模式用replace无法替换，所以用上了re.sub
        author_split_char = self._get_author_split_char(article_info)
        author = author.replace("<br>", "").strip()
        authors = author.split(author_split_char)
        format_authors = []
        format_sups = []
        for author in authors:
            author_sup = re.findall("<sup>([\w\-, ]+)</sup>", author)
            author_sup = [self._format_author_sup(sup) for sup in author_sup]
            author = re.sub("<sup>[\w\-, ]+</sup>", "", author).strip().strip(".")
            #sys.exit(1)
            format_authors.append(author)
            format_sups.append(",".join(author_sup))
        return format_authors, format_sups

    def _format_author_affiliations_by_author(self, author_affiliation, author):
        """
        for example:
            input:
                author:[u'Elizabeth J. Opperman', u' Michael I. Cherry', u' Nokwanda P. Makunga']
                author_affiliation:'Elizabeth J. Opperman, Department of Botany and Zoology, Stellenbosch University, South Africa Michael I. Cherry, Department of Botany and Zoology, Stellenbosch University, South Africa Nokwanda P. Makunga, Department of Botany and Zoology, Stellenbosch University, South Africa'
            return:
                author_affiliation:[
                    "Department of Botany and Zoology, Stellenbosch University, South Africa",
                    "Department of Botany and     Zoology, Stellenbosch University, South Africa",
                    "Department of Botany and Zoology, Stellenbosch University, South Africa"]
        """
        author_affiliations = []
        author_index = 0
        while author_index < len(author):
          author_name = author[author_index] 
          start_index = author_affiliation.find(author_name)
          if start_index == -1:
            raise Exception("cannot find author in affliication: %s" % author_name)

          start_index = start_index + len(author_name)
          if author_index == len(author) -1:
            affiliation = author_affiliation[start_index:]
          else:
            end_index = author_affiliation.find(author[author_index + 1])
            if end_index == -1:
              raise Exception("cannot find author in affliication: %s" % author[author_index + 1])
            affiliation = author_affiliation[start_index:end_index]

          affiliation = affiliation.strip(",").strip()
          
          author_affiliations.append(affiliation)
          author_index += 1
        return author_affiliations

    def _format_author_affiliations(self, article_info):
        """
        for example:
            input:
                article_info['author_affiliation']: ["<sup>a</sup>Department of Pharmacology, Postgraduate Institute of Medical Education and Research and Dr. Ram Manohar Lohia Hospital, New Delhi, and <sup>b</sup>Department of Pharmacology, Gauhati Medical College and Hospital, Guwahati, India"]
            return:
                author_affiliation:[
                    "Department of Pharmacology, Postgraduate Institute of Medical Education and Research and Dr. Ram Manohar Lohia Hospital, New Delhi",
                    "Department of Pharmacology, Gauhati Medical College and Hospital, Guwahati, India"]
        """
        author_affiliation = article_info["author_affiliation"][0]
        author_affiliations = []
        sup_start_chars = "<sup>"
        sup_end_chars = "</sup>"
        index = 0
        sup_start_index = author_affiliation.find(sup_start_chars, index)
        sup_end_index = 0
        if sup_start_index == -1:
            return article_info["author_affiliation"]

        while sup_start_index != -1:
            sup_end_index = author_affiliation.index(sup_end_chars, sup_start_index)
            sup_start_index = author_affiliation.find(sup_start_chars, sup_end_index + len(sup_end_chars))
            if sup_start_index != -1:
                author_affiliations.append(author_affiliation[sup_end_index + len(sup_end_chars): sup_start_index])
            else: 
                author_affiliations.append(author_affiliation[sup_end_index + len(sup_end_chars):])
        return author_affiliations
    def _format_author_sup(self, origin_sup):
        """
        Format author sup
        for example:
            case 1:
                origin_sup: a-c,d
                return: 1,2,3,4
            case 2:
                origin_sup: 1-4
                return: 1,2,3,4
        """
        origin_sup = origin_sup.encode("utf-8").replace(" ", "").replace("–", "-").strip("").strip(",").replace(",", "-")
        origin_sup = "".join([str(ord(sup) - ord('a') + 1) if sup.isalpha() else sup for sup in origin_sup])
        origin_sup = Utils.regex_extract(origin_sup, "\w*(\d+)")
        if origin_sup == "":
            origin_sup = '1'
        sups = origin_sup.split(",")
        res = []
        for sup in sups:
            if sup.find("-") != -1:
                elems = sup.split("-")
                if len(elems) != 2:
                    raise Exception("unexcept sup: %s" % origin_sup)
                start = int(elems[0])
                end = int(elems[1])
                res.extend(range(start, end + 1))
            else:
                res.append(sup)

        ret = ",".join([str(e) for e in res])    
        return ret
    def _mark_bad_record(self, bad_record):
        """
        Mark an bad record

        @param bad_record, format:{"reason: ", "url"}
        """
        bad_record_str = json.dumps(bad_record)
        self.bad_meta_writer.write(bad_record_str)
        self.bad_meta_writer.write("\n")

def parse_init():
    """
    Init argument parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', "--action", default='meta_check', help="action to perform",                              
                choices=['meta_check', 'check_miss_journal', 'check_miss_url'])
    parser.add_argument('-f', "--file", required=True, help="meta file path")
    parser.add_argument('-d', "--pdf_dir", required=False, help="pdf save dir")
    parser.add_argument('-p', "--pass_meta_file", default="pass_meta", help="file to save pass meta")
    parser.add_argument('-b', "--bad_meta_file", default="bad_meta", help="file to save bad meta")
    parser.add_argument('-m', "--miss_pdf_file", default="miss_pdf_file", help="pdf link that fail to download")
    parser.add_argument('-j', "--journal_file", help="journal file, xls format")
    parser.add_argument('-u', "--url_file", help="url_file")
    parser.add_argument('-s', "--source_name", help="source name[f.e: wiley]")
    parser.add_argument('-o', "--for_oa", default="False", help="if conerted meta used for oa")
    return parser

def select_action(action):
    """
    select action
    """
    return {
        'meta_check': meta_check.start,
        'check_miss_journal': meta_check.check_miss_journal,
        'check_miss_url': meta_check.check_miss_url
    }.get(action, meta_check.start)
    
if __name__ == '__main__':
    meta_file = sys.argv[1]
    args = parse_init().parse_args()
    meta_check = MetaCheck(args)
    ret = select_action(args.action)()
    exit(ret)
    meta_check.start()
