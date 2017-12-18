# -*- coding: utf-8 -*- 
import os
import sys
import json
import time
import xlrd
import datetime
import re
from xml.dom import minidom
from mysql_helper import MySQLHelper
reload(sys)
sys.setdefaultencoding('utf8')

class Json2Xml:
    """Convert metadata result crawled by scrapy to xml
    """
    def __init__(self, all_journal_meta_xls, json_file, save_file):
        self.json_file = json_file
        self.save_file = save_file
        self.today = '20171112'
        self.now = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))

        self.all_journal_meta = {}
        self.load_journal_meta(all_journal_meta_xls)
        self.journal_ids = {}
        self.next_article_id= 1
        self.current_url = ""
        self.journal_name_map = {
            "C" : "c journal of carbon research",
            "IJERPH" : "International Journal of Environmental Research and Public Health",
            "IJFS" : "International Journal of Financial Studies",
            "IJGI" : "ISPRS International Journal of Geo-Information",
            "IJMS" : "International Journal of Molecular Sciences",
            "J. INTELL." : "Journal of Intelligence",
            "JCDD" : "Journal of Cardiovascular Development and Disease",
            "JCM" : "Journal of Clinical Medicine",
            "JDB" : "Journal of Developmental Biology",
            "JFB" : "Journal of Functional Biomaterials",
            "JLPEA" : "Journal of Low Power Electronics and Applications",
            "JMSE" : "Journal of Marine Science and Engineering",
            "JPM" : "Journal of Personalized Medicine",
            "JRFM" : "Journal of Risk and Financial Management",
            "JSAN" : "Journal of Sensor and Actuator Networks",
        }
        print self.journal_name_map

        self._init_db()

    def __del__(self):
        self.mysql_helper.close()

    """
    Init mysql database and table:
    1. create database oa if not exist
    2. create table article_info if not exist
    3. create table article_author if not exist
    """
    def _init_db(self):
            self.mysql_helper = MySQLHelper("localhost", "root", "123456")
            self.oa_database = "oa"
            self.article_table = "article_info"
            self.author_table = "article_author"
            self.mysql_helper.create_database(self.oa_database)
            self.mysql_helper.use_db(self.oa_database)
            create_table_sql = "create table if not exists %s(" \
                                "collection_id varchar(50) NOT NULL," \
                                "source_id varchar(50) NOT NULL,"\
                                "system_id varchar(50) NOT NULL,"\
                                "ro_id varchar(50) NOT NULL,"\
                                "work_id varchar(50) NOT NULL,"\
                                "doi varchar(100) NOT NULL,"\
                                "work_title text NOT NULL,"\
                                "issn varchar(20),"\
                                "eissn varchar(20),"\
                                "collection_title varchar(100) NOT NULL,"\
                                "platform_url varchar(100) NOT NULL,"\
                                "source_name varchar(100) NOT NULL,"\
                                "keywords text,"\
                                "language varchar(20) NOT NULL,"\
                                "abstract text,"\
                                "country varchar(20) NOT NULL,"\
                                "publish_year varchar(20) NOT NULL,"\
                                "publish_date varchar(20) NOT NULL,"\
                                "volume varchar(10) NOT NULL,"\
                                "issue varchar(10) NOT NULL,"\
                                "access_url varchar(300) NOT NULL,"\
                                "license_text text,"\
                                "license_url varchar(100),"\
                                "copyright text,"\
                                "ro_title varchar(100) NOT NULL,"\
                                "xml_uri varchar(300) NOT NULL,"\
                                "pdf_uri varchar(300) NOT NULL,"\
                                "pdf_access_url varchar(200) NOT NULL,"\
                                "creator varchar(20) NOT NULL,"\
                                "create_time datetime NOT NULL,"\
                                "finished tinyint(1) NOT NULL DEFAULT 0,"\
                                "extra varchar(50) comment 'extra info',"\
                                "PRIMARY KEY(work_id)) DEFAULT CHARSET=utf8;" % self.article_table
            self.mysql_helper.execute(create_table_sql)

            author_create_table_sql = "create table if not exists %s("\
                                      "work_id varchar(50) NOT NULL,"\
                                      "author_name varchar(100) NOT NULL,"\
                                      "institution_name varchar(500),"\
                                      "PRIMARY KEY(work_id, author_name, institution_name)) DEFAULT CHARSET=utf8;" % self.author_table
            self.mysql_helper.execute(author_create_table_sql)


    def convert(self):
        output_meta_file_path = "%s/output_meta.jl" % self.save_file
        author_meta_file_path = "%s/author_meta.txt" % self.save_file

        self.output_meta_file = open(output_meta_file_path, 'w')
        self.author_meta_file = open(author_meta_file_path, 'w')

        meta_format_error = 0 
        with open(self.json_file) as fp:
            for line in fp:
                try:
                    article_info = json.loads(line)
                except Exception as e:
                    meta_format_error = meta_format_error + 1
                    continue
                    
                self.convert_to_xml(article_info)

        self.output_meta_file.close()
        self.author_meta_file.close()
        print "meta_format_error :%d" % meta_format_error

    def convert_from_database(self):
        #sql = "select collection_title from article_info where collection_title like '%cadernos de sa%' limit 1"
        #collection_titles = self.mysql_helper.query_all(sql)
        #for collection_title in collection_titles:
        #    collection_title = collection_title['collection_title'].encode("utf-8")
        #    print collection_title
        #sys.exit(0)

        article_info_table = "article_info_test"
        author_sql = "select * from article_author where work_id in (select work_id from %s)" % article_info_table
        authors = self.mysql_helper.query_all(author_sql)
        self.author_map = {}

        for author in authors:
            work_id = author['work_id']

            if work_id not in self.author_map:
                self.author_map[work_id] = [author]
            else:
                self.author_map[work_id].append(author)

        sql = "select * from article_info_test"
        articles = self.mysql_helper.query_all(sql)
        for article_info in articles:
            self.convert_to_xml_from_database(article_info)

    def convert_to_xml_from_database(self, article_info):
        source_name_str = "Scielo"
        url = self.get_article_field(article_info, "access_url")
        self.url = url
        self.current_url = url
        print "process %s" % url
        volume = self.get_article_field(article_info, "volume").replace("vol.", "").strip()
        issue = self.get_article_field(article_info, "issue").replace("no.", "")

        journal_name = self.get_article_field(article_info, "collection_title").lower().encode("utf-8")
        available_time_text = 'Before-Publication-OA'
        doi = self.get_article_field(article_info, "doi")
        title = self.get_article_field(article_info, "work_title")
        abstract = self.get_article_field(article_info, "abstract")
        xlink = self.get_article_field(article_info, "license_url")
        license_text = self.get_article_field(article_info, "license_text")
        copyright_text = self.get_article_field(article_info, "copyright") 
        publish_date  = self.get_article_field(article_info, "publish_date")

        #publish_date比如是2017-12-18这种格式,如果缺少『日』,那么就默认为1
        publish_date_elems = publish_date.split('-')
        print "publish_date: %s" % publish_date
        if len(publish_date_elems) == 1:
            pass
        elif len(publish_date_elems) == 2:
            publish_date = publish_date + "-1"
            publish_date = "%s-%02d" % (int(publish_date_elems[0]), int(publish_date_elems[1])) 
        elif len(publish_date_elems) == 3:
            publish_date = "%s-%02d-%02d" % (publish_date_elems[0], int(publish_date_elems[1]), int(publish_date_elems[2]))
        else:
            raise Exception("unexcept publish date format :%s, %s" % (publish_date, self.url))

        pdf_link = self.get_article_field(article_info, "pdf_access_url")
        keywords = self.get_article_field(article_info, "keywords")

        issue_dir = self.get_article_field(article_info, "xml_uri")
        issue_dir = os.path.dirname(issue_dir)
        if not os.path.exists(issue_dir):
            os.makedirs(issue_dir)

        article_id = self.get_article_field(article_info, "work_id")
        pdf_name = self.get_article_field(article_info, "ro_title")
        xml_file_path = self.get_article_field(article_info, "xml_uri")
        pdf_file_path = self.get_article_field(article_info, "pdf_uri")
        create_time_text = self.get_article_field(article_info, "create_time")

        #create time必须按照格式来，不然xml校验通过不了
        print "create time :%s" % create_time_text
        create_time_obj = datetime.datetime.strptime(str(create_time_text), "%Y-%m-%d %H:%M:%S")
        create_time_text = create_time_obj.strftime('%Y-%m-%dT%H:%M:%S')

        creator = self.get_article_field(article_info, "creator")
        collection_id_text = self.get_article_field(article_info, "collection_id")
        source_id_text = self.get_article_field(article_info, "source_id")
        system_id = self.get_article_field(article_info, "system_id")
        ro_id = self.get_article_field(article_info, "ro_id")
        issn = self.get_article_field(article_info, "issn")
        eissn = self.get_article_field(article_info, "eissn")
        platform_url = self.get_article_field(article_info, "platform_url")
        language = self.get_article_field(article_info, "language")
        country_text = self.get_article_field(article_info, "country")
        publish_year_text = self.get_article_field(article_info, "publish_year")

        #2. create xml for this article
        doc = minidom.Document()
        root = doc.createElement('nstl_ors:work_group')
        doc.appendChild(root)
        root.setAttribute("xmlns:nstl", "http://spec.nstl.gov.cn/specification/namespace")
        root.setAttribute("xmlns:nstl_ors", "http://open-resources.nstl.gov.cn/elements/2015")
        root.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.setAttribute("xmlns:xml", "http://www.w3.org/XML/1998/namespace")
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.setAttribute("xsi:schemaLocation", "http://open-resources.nstl.gov.cn/elements/2015")

        work_meta = doc.createElement("nstl_ors:work_meta")
        root.appendChild(work_meta)

        # Add collection meta
        collection_meta = doc.createElement("nstl_ors:collection_meta")
        work_meta.appendChild(collection_meta)
        collection_id = doc.createElement("nstl_ors:collection_id")
        collection_meta.appendChild(collection_id)
        text = doc.createTextNode(collection_id_text)
        collection_id.appendChild(text)
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_meta.appendChild(collection_id_other)
        collection_id_other.appendChild(doc.createTextNode(system_id))
        collection_id_other.setAttribute("identifier-type", 'SystemID')
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_meta.appendChild(collection_id_other)
        collection_id_other.appendChild(doc.createTextNode(issn))
        collection_id_other.setAttribute("identifier-type", 'ISSN')
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_id_other.appendChild(doc.createTextNode(eissn))
        collection_id_other.setAttribute("identifier-type", 'EISSN')
        collection_meta.appendChild(collection_id_other)
        collection_title = doc.createElement("nstl_ors:collection_title")
        collection_title.appendChild(doc.createCDATASection(journal_name))
        collection_meta.appendChild(collection_title)
        collection_publiction_type = doc.createElement("nstl_ors:publication_type")
        collection_publiction_type.appendChild(doc.createTextNode("Journal"))
        collection_meta.appendChild(collection_publiction_type)
        access_group = doc.createElement("nstl_ors:access_group")
        collection_meta.appendChild(access_group)
        access_meta = doc.createElement("nstl_ors:access_meta")
        access_group.appendChild(access_meta)
        access_url = doc.createElement("nstl_ors:access_url")
        access_url.appendChild(doc.createCDATASection(platform_url))
        access_meta.appendChild(access_url)
        source_meta = doc.createElement("nstl_ors:source_meta")
        access_meta.appendChild(source_meta)
        source_id = doc.createElement("nstl_ors:source_id")
        source_meta.appendChild(source_id)
        source_id.appendChild(doc.createTextNode(source_id_text))
        source_name = doc.createElement("nstl_ors:source_name")
        source_meta.appendChild(source_name)
        source_name.appendChild(doc.createCDATASection(source_name_str))
        source_type = doc.createElement("nstl_ors:souce_type")
        source_meta.appendChild(source_type)
        source_type.appendChild(doc.createTextNode("Publisher"))

        work_id = doc.createElement("nstl_ors:work_id")
        work_meta.appendChild(work_id)
        work_id.appendChild(doc.createTextNode(article_id))
        work_id_other = doc.createElement("nstl_ors:work_id_other")
        work_meta.appendChild(work_id_other)
        work_id_other.appendChild(doc.createTextNode(doi))
        work_id_other.setAttribute("identifier-type", "DOI")
        work_title = doc.createElement("nstl_ors:work_title")
        work_meta.appendChild(work_title)
        work_title.appendChild(doc.createCDATASection(title))
        publication_type = doc.createElement("nstl_ors:publication_type")
        work_meta.appendChild(publication_type)
        publication_type.appendChild(doc.createTextNode("JournalArticle"))
        contributer_group = doc.createElement("nstl_ors:contributer_group")
        work_meta.appendChild(contributer_group)
        index = 0

        if article_id not in self.author_map:
            raise Exception("cannot find author info for work_id :%s" % work_id)

        author_infos = {}
        for author in self.author_map[article_id]:
            author_name = author['author_name']
            institution_name = author['institution_name']
            
            if author_name not in author_infos:
                author_infos[author_name] = [institution_name]
            else:
                author_infos[author_name].append(institution_name)

        for author, institutions in author_infos.items():
            contributer_meta = doc.createElement("nstl_ors:contributer_meta")
            contributer_group.appendChild(contributer_meta)
            name = doc.createElement("nstl_ors:name")
            contributer_meta.appendChild(name)
            name.appendChild(doc.createCDATASection(author))
            role = doc.createElement("nstl_ors:role")
            contributer_meta.appendChild(role)
            role.appendChild(doc.createTextNode("Author"))
            affiliation = doc.createElement("nstl_ors:affiliation")
            contributer_meta.appendChild(affiliation)
            institution_meta = doc.createElement("nstl_ors:institution-meta")
            affiliation.appendChild(institution_meta)
            for institution in institutions:
                institution_name = doc.createElement("nstl_ors:institution_name")
                institution_meta.appendChild(institution_name)
                institution_name.appendChild(doc.createCDATASection(institution))

        keywords_group = doc.createElement("nstl_ors:kwd-group")
        work_meta.appendChild(keywords_group)
        keywords = keywords.split(";")
        for keyword_txt in keywords:
            if keyword_txt is None:
                keyword_txt = ""
            keyword = doc.createElement("nstl_ors:keyword")
            keywords_group.appendChild(keyword)
            keyword.appendChild(doc.createCDATASection(keyword_txt)) 
        
        language = doc.createElement("nstl_ors:language")
        work_meta.appendChild(language)
        language.appendChild(doc.createTextNode("eng"))

        abstract_node = doc.createElement("nstl_ors:abstract")
        work_meta.appendChild(abstract_node)
        abstract_node.appendChild(doc.createCDATASection(abstract)) 

        #TODO页码
        #total_page_number = doc.createElement("nstl_ors:total_page_number")
        #work_meta.appendChild(total_page_number)
        #total_page_number.appendChild(doc.createTextNode("1"))
        #start_page = doc.createElement("nstl_ors:start_page")
        #work_meta.appendChild(start_page)
        #start_page.appendChild(doc.createTextNode("1"))
        #end_page = doc.createElement("nstl_ors:end_page")
        #work_meta.appendChild(end_page)
        #end_page.appendChild(doc.createTextNode("1"))

        country = doc.createElement("nstl_ors:country")
        work_meta.appendChild(country)
        country.appendChild(doc.createTextNode(country_text))

        publication_year = doc.createElement("nstl_ors:publication_year")
        work_meta.appendChild(publication_year)
        publication_year.appendChild(doc.createTextNode(publish_year_text))
        
        volumn_node = doc.createElement("nstl_ors:volume")
        work_meta.appendChild(volumn_node)
        volumn_node.appendChild(doc.createTextNode(volume))

        issue_node = doc.createElement("nstl_ors:issue")
        work_meta.appendChild(issue_node)
        issue_node.appendChild(doc.createTextNode(issue))

        publish_date_node = doc.createElement("nstl_ors:publication_date")
        work_meta.appendChild(publish_date_node)
        publish_date_node.appendChild(doc.createTextNode(publish_date))

        self_url = doc.createElement("nstl_ors:self-uri")
        work_meta.appendChild(self_url)
        self_url.setAttribute("content-type", "XML")
        self_url.setAttribute("xlink:href", xml_file_path)

        access_group = doc.createElement("nstl_ors:access_group")
        work_meta.appendChild(access_group)

        access_meta = doc.createElement("nstl_ors:access_meta")
        access_group.appendChild(access_meta)
        access_url = doc.createElement("nstl_ors:access_url")
        access_meta.appendChild(access_url)
        access_url.appendChild(doc.createCDATASection(url))
        permissions_meta = doc.createElement("nstl_ors:permissions_meta")
        access_meta.appendChild(permissions_meta)
        copyright_statement = doc.createElement("nstl_ors:copyright-statement")
        if copyright_text != "":
            copyright_text = "no copyright"
        permissions_meta.appendChild(copyright_statement)
        copyright_statement.appendChild(doc.createCDATASection(copyright_text))
        license = doc.createElement("nstl_ors:license")
        permissions_meta.appendChild(license)
        #TODO 通过检查的没加这个
        #license.setAttribute("license-type", journal_meta['license_type'])
        license.setAttribute("xlink:href", xlink)
        license.appendChild(doc.createCDATASection(license_text))
        available_time = doc.createElement("nstl_ors:available_time")
        #TODO
        #permissions_meta.appendChild(available_time)
        available_time.appendChild(doc.createTextNode(available_time_text))
        oa_type = doc.createElement("nstl_ors:OA-type")
        #permissions_meta.appendChild(oa_type)
        #TODO
        #oa_type.appendChild(doc.createTextNode(journal_meta['oa_type']))

        #TODO what's this?
        related_object_group = doc.createElement("nstl_ors:related_object_group")
        work_meta.appendChild(related_object_group)
        related_object = doc.createElement("nstl_ors:related_object")
        related_object_group.appendChild(related_object)
        ro_id = doc.createElement("nstl_ors:ro_id")
        related_object.appendChild(ro_id)
        #TODO PDF的ID和Article的ID取一样的，其他需求可能不适用
        ro_id.appendChild(doc.createTextNode(pdf_name))
        ro_title = doc.createElement("nstl_ors:ro_title")
        related_object.appendChild(ro_title)
        ro_title.appendChild(doc.createTextNode(pdf_name))
        ro_type = doc.createElement("nstl_ors:ro_type")
        #TODO
        #related_object.appendChild(ro_type)
        ro_type.appendChild(doc.createTextNode("CompleteContent"))
        media_type = doc.createElement("nstl_ors:media_type")
        related_object.appendChild(media_type)
        media_type.appendChild(doc.createTextNode("PDF"))
        ro_self_url = doc.createElement("nstl_ors:self-uri") 
        related_object.appendChild(ro_self_url)
        ro_self_url.setAttribute("content-type", "PDF")
        ro_self_url.setAttribute("xlink:href", pdf_file_path)  
        ro_access_meta = doc.createElement("nstl_ors:access_meta")
        related_object.appendChild(ro_access_meta)
        ro_access_url = doc.createElement("nstl_ors:access_url")
        ro_access_meta.appendChild(ro_access_url)
        ro_access_url.appendChild(doc.createCDATASection(pdf_link))

        management_meta = doc.createElement("nstl_ors:management-meta")
        work_meta.appendChild(management_meta)
        creator = doc.createElement("nstl_ors:creator")
        management_meta.appendChild(creator)
        creator.appendChild(doc.createTextNode("NK"))
        create_time = doc.createElement("nstl_ors:create_time")
        management_meta.appendChild(create_time)
        create_time.appendChild(doc.createTextNode(str(create_time_text)))
        revision_time = doc.createElement("nstl_ors:revision_time")
        #TODO
        #management_meta.appendChild(revision_time)
        revision_time.appendChild(doc.createTextNode(str(create_time_text)))

        #print article_info
        print "save to :%s" % xml_file_path
        xml_str = doc.toprettyxml(indent="  ").encode('utf-8')
        with open(xml_file_path, "w") as f:
            f.write(xml_str)

    def convert_to_xml(self, article_info):
        source_name_str = "Scielo"

        url = self.get_article_field(article_info, "url")
        self.url = url
        volume = self.get_article_field(article_info, "volumn").replace("vol.", "").strip()
        issue = self.get_article_field(article_info, "issue").replace("no.", "")
        if volume == "" or issue == "": 
            print "invalid volume and issue(%s, %s): %s" % (volume, issue, self.url)
            return
        journal_name = self.get_article_field(article_info, "journal")
        doi = self.get_article_field(article_info, "doi")
        title = self.get_article_field(article_info, "title")
        abstract = self.get_article_field(article_info, "abstract", throw_exception = False).replace("View Full-Text", "").strip()
        if abstract == "":
            print "abstract is empty: %s" % self.url
            return
        try:
            date = self.get_article_field(article_info, "date")
        except Exception  as e:
            print "date is empty: %s" % self.url
            return
            
        xlink = self.get_article_field(article_info, "xlink", throw_exception = False)
        if xlink == "":
            xlink = "https://creativecommons.org/licenses/by/4.0/"
        license_text = self.get_article_field(article_info, "license", throw_exception = False)
        if license_text == "":
            license_text = "This is an open access article distributed under the Creative Commons Attribution License which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited. (CC BY 4.0)."
        copyright_text = self.get_article_field(article_info, "copyright", throw_exception = False)
        self.current_url = url

        journal_not_found = False
        if (journal_name.lower() not in self.all_journal_meta):
            if journal_name.upper() in self.journal_name_map:
                converted_journal_name = self.journal_name_map[journal_name.upper()]
                if converted_journal_name.lower() not in self.all_journal_meta:
                    print "cannot find meta info for converted_journal_name journal: %s" % converted_journal_name.lower()
                    journal_not_found = True
                else:
                    journal_name = converted_journal_name
            else:
                print "cannot find meta info for journal: %s" % (journal_name.encode('utf-8').upper())
                journal_not_found = True

        if journal_not_found:
            #raise Exception("cannot find meta info for journal: %s" % journal_name)
            #print "cannot find meta info for journal: %s,%s" % (journal_name, url)
            print "cannot find meta info for journal: %s" % (journal_name.encode('utf-8'))
            return
            
        journal_meta = self.all_journal_meta[journal_name.lower()]

        #Anthor journal publish date may not like "18 August 2017"
        publish_date  = self.get_article_field(article_info, "publish_date")
        #try:
        #    publish_date = datetime.datetime.strptime(publish_date, "%d %B %Y").strftime("%Y-%m-%d")
        #except Exception as e:
        #    #print "publish date unexpected %s, url is %s" % (publish_date, url)
        #    #return
        #    publish_date = "no publish date"
            
            

        try:
            pdf_link = self.get_article_field(article_info, "pdf_link")
        except Exception as e:
            print "cannot find pdf_link: %s" % self.url
            return

        keywords = self.get_article_field(article_info, "keywords", False, throw_exception = False)
        if (keywords == ""):
            print "cannot find keywords: %s" % self.url
            return

        try:
            authors = self.get_article_field(article_info, "author", False)
            author_sup = self.get_article_field(article_info, "author_sup", False)
            author_sup = self.format_author_sup(len(authors), author_sup)
            author_affiliation = self.get_article_field(article_info, "author_affiliation", False)
            author_affiliation = filter(lambda x: self.filter_author_affiliation(x), author_affiliation)
        except Exception as e:
            print "author_affiliation is miss :%s" % self.url
            return
        
        output_meta = {}

        if len(authors) != len(author_sup):
            print "authors and authos_sup len not equal, This not gonna happen: %s" % url
            return
        
        if len(author_sup) < 1:
            print "no author, not gonna happen :%s" % url
            return

        if date == "":
            print "date is empty: %s" % url
            return

        if (int(date) < 2015):
            print "too old issue: %s" % date
            #ignore too old issue
            return

        if source_name_str == "Scielo":
            url_pattern = re.compile(r".*script=.*&pid=S.{4}\-.{4}(?P<date>\d{4}).{9}&lng=.*")
            m = url_pattern.match(url)
            if m is None:
                raise Exception("url not match pattern :%s" % url)

            date = m.group('date')

        #1. create issue dir
        issue_dir = "%s/%s^Y%s^V%s^N%s" % (self.save_file, journal_meta['collection_id'], date, volume, issue)
        if not os.path.exists(issue_dir):
            os.makedirs(issue_dir)

        article_id = self.generate_article_id()
        pdf_name = article_id.replace("JA", "RO")
        xml_file_path = "%s/%s.xml" % (issue_dir, article_id)
        pdf_file_path = "Files/%s.pdf" % pdf_name

        #2. create xml for this article
        doc = minidom.Document()
        root = doc.createElement('nstl_ors:work_group')
        doc.appendChild(root)
        root.setAttribute("xmlns:nstl", "http://spec.nstl.gov.cn/specification/namespace")
        root.setAttribute("xmlns:nstl_ors", "http://open-resources.nstl.gov.cn/elements/2015")
        root.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        root.setAttribute("xmlns:xml", "http://www.w3.org/XML/1998/namespace")
        root.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.setAttribute("xsi:schemaLocation", "http://open-resources.nstl.gov.cn/elements/2015")

        work_meta = doc.createElement("nstl_ors:work_meta")
        root.appendChild(work_meta)

        # Add collection meta
        collection_meta = doc.createElement("nstl_ors:collection_meta")
        work_meta.appendChild(collection_meta)
        collection_id = doc.createElement("nstl_ors:collection_id")
        collection_meta.appendChild(collection_id)
        text = doc.createTextNode(journal_meta['collection_id'])
        collection_id.appendChild(text)
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_meta.appendChild(collection_id_other)
        collection_id_other.appendChild(doc.createTextNode(journal_meta['system_id']))
        collection_id_other.setAttribute("identifier-type", 'SystemID')
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_meta.appendChild(collection_id_other)
        collection_id_other.appendChild(doc.createTextNode(journal_meta['issn']))
        collection_id_other.setAttribute("identifier-type", 'ISSN')
        collection_id_other = doc.createElement("nstl_ors:collection_id_other")
        collection_id_other.appendChild(doc.createTextNode(journal_meta['eissn']))
        collection_id_other.setAttribute("identifier-type", 'EISSN')
        collection_meta.appendChild(collection_id_other)
        collection_title = doc.createElement("nstl_ors:collection_title")
        collection_title.appendChild(doc.createCDATASection(journal_name))
        collection_meta.appendChild(collection_title)
        collection_publiction_type = doc.createElement("nstl_ors:publication_type")
        collection_publiction_type.appendChild(doc.createTextNode("Journal"))
        collection_meta.appendChild(collection_publiction_type)
        access_group = doc.createElement("nstl_ors:access_group")
        collection_meta.appendChild(access_group)
        access_meta = doc.createElement("nstl_ors:access_meta")
        access_group.appendChild(access_meta)
        access_url = doc.createElement("nstl_ors:access_url")
        access_url.appendChild(doc.createCDATASection(journal_meta['platform_url']))
        access_meta.appendChild(access_url)
        source_meta = doc.createElement("nstl_ors:source_meta")
        access_meta.appendChild(source_meta)
        source_id = doc.createElement("nstl_ors:source_id")
        source_meta.appendChild(source_id)
        #TODO JOURNAL的Source ID需要拿到
        source_id.appendChild(doc.createTextNode(journal_meta['source_id']))
        source_name = doc.createElement("nstl_ors:source_name")
        source_meta.appendChild(source_name)
        source_name.appendChild(doc.createCDATASection(source_name_str))
        source_type = doc.createElement("nstl_ors:souce_type")
        source_meta.appendChild(source_type)
        source_type.appendChild(doc.createTextNode("Publisher"))

        work_id = doc.createElement("nstl_ors:work_id")
        work_meta.appendChild(work_id)
        work_id.appendChild(doc.createTextNode(article_id))
        work_id_other = doc.createElement("nstl_ors:work_id_other")
        work_meta.appendChild(work_id_other)
        work_id_other.appendChild(doc.createTextNode(doi))
        work_id_other.setAttribute("identifier-type", "DOI")
        work_title = doc.createElement("nstl_ors:work_title")
        work_meta.appendChild(work_title)
        work_title.appendChild(doc.createCDATASection(title))
        publication_type = doc.createElement("nstl_ors:publication_type")
        work_meta.appendChild(publication_type)
        publication_type.appendChild(doc.createTextNode("JournalArticle"))
        contributer_group = doc.createElement("nstl_ors:contributer_group")
        work_meta.appendChild(contributer_group)
        index = 0
        for author in authors:
            contributer_meta = doc.createElement("nstl_ors:contributer_meta")
            contributer_group.appendChild(contributer_meta)
            #TODO 通过检查的xml没有加这个属性
            name = doc.createElement("nstl_ors:name")
            contributer_meta.appendChild(name)
            name.appendChild(doc.createCDATASection(author))
            role = doc.createElement("nstl_ors:role")
            contributer_meta.appendChild(role)
            role.appendChild(doc.createTextNode("Author"))
            affiliation = doc.createElement("nstl_ors:affiliation")
            contributer_meta.appendChild(affiliation)
            affiliation_index = author_sup[index]
            institution_meta = doc.createElement("nstl_ors:institution-meta")
            affiliation.appendChild(institution_meta)
            for aff_index in affiliation_index.split(','):
                institution_name = doc.createElement("nstl_ors:institution_name")
                institution_meta.appendChild(institution_name)
                try:
                    institution_name.appendChild(doc.createCDATASection(author_affiliation[int(aff_index)-1]))
                except:
                    print "catch exception when add authori %s" % url
                    #print article_info
                    #raise Exception("catch exception when add author")
                    return
                author_meta = {}
                author_meta['work_id'] = article_id
                author_meta['author_name'] = author
                author_meta['institution_name'] = author_affiliation[int(aff_index)-1]
                self.save_article_author_info(author_meta)
                #self.author_meta_file.write("%s@@%s@@%s"%(article_id, author.encode('utf-8'), author_affiliation[int(aff_index)-1].encode('utf-8')))
                #self.author_meta_file.write('\n')
           

            #TODO 通过检查的xml，作者的标注不一样
            #xref = doc.createElement("nstl_ors:xref")
            #contributer_meta.appendChild(xref)
            #xref.setAttribute("ref-type", "institution-meta")
            #affiliation_index = author_sup[index]
            #affiliation_index = ','.join(['I'+ k for k in affiliation_index.split(',')])
            #xref.setAttribute("rid", affiliation_index)
            #index = index + 1

        #TODO 通过检查的xml，作者的标注还不一样
        #institution_group = doc.createElement("nstl_ors:institution_group")
        #work_meta.appendChild(institution_group)
        #institution_index = 0
        #for affliation in author_affiliation:
        #    institution_meta = doc.createElement("nstl_ors:institution-meta")
        #    institution_group.appendChild(institution_meta)
        #    institution_meta.setAttribute("inst_id", 'I' + str(institution_index + 1))
        #    
        #    institution_name = doc.createElement("nstl_ors:institution_name")
        #    institution_meta.appendChild(institution_name)
        #    institution_name.appendChild(doc.createCDATASection(author_affiliation[institution_index]))
        #    institution_index = institution_index + 1

        keywords_group = doc.createElement("nstl_ors:kwd-group")
        work_meta.appendChild(keywords_group)
        for keyword_txt in keywords:
            if keyword_txt is None:
                keyword_txt = ""
            keyword = doc.createElement("nstl_ors:keyword")
            keywords_group.appendChild(keyword)
            keyword.appendChild(doc.createCDATASection(keyword_txt)) 
        
        language = doc.createElement("nstl_ors:language")
        work_meta.appendChild(language)
        language.appendChild(doc.createTextNode("eng"))

        abstract_node = doc.createElement("nstl_ors:abstract")
        work_meta.appendChild(abstract_node)
        abstract_node.appendChild(doc.createCDATASection(abstract)) 

        #TODO页码
        #total_page_number = doc.createElement("nstl_ors:total_page_number")
        #work_meta.appendChild(total_page_number)
        #total_page_number.appendChild(doc.createTextNode("1"))
        #start_page = doc.createElement("nstl_ors:start_page")
        #work_meta.appendChild(start_page)
        #start_page.appendChild(doc.createTextNode("1"))
        #end_page = doc.createElement("nstl_ors:end_page")
        #work_meta.appendChild(end_page)
        #end_page.appendChild(doc.createTextNode("1"))

        country = doc.createElement("nstl_ors:country")
        work_meta.appendChild(country)
        country.appendChild(doc.createTextNode(journal_meta['country']))

        publication_year = doc.createElement("nstl_ors:publication_year")
        work_meta.appendChild(publication_year)
        publication_year.appendChild(doc.createTextNode(date))
        
        volumn_node = doc.createElement("nstl_ors:volume")
        work_meta.appendChild(volumn_node)
        volumn_node.appendChild(doc.createTextNode(volume))

        issue_node = doc.createElement("nstl_ors:issue")
        work_meta.appendChild(issue_node)
        issue_node.appendChild(doc.createTextNode(issue))

        publish_date_node = doc.createElement("nstl_ors:publication_date")
        work_meta.appendChild(publish_date_node)
        publish_date_node.appendChild(doc.createTextNode(publish_date))

        self_url = doc.createElement("nstl_ors:self-uri")
        work_meta.appendChild(self_url)
        self_url.setAttribute("content-type", "XML")
        self_url.setAttribute("xlink:href", xml_file_path)

        access_group = doc.createElement("nstl_ors:access_group")
        work_meta.appendChild(access_group)

        access_meta = doc.createElement("nstl_ors:access_meta")
        access_group.appendChild(access_meta)
        access_url = doc.createElement("nstl_ors:access_url")
        access_meta.appendChild(access_url)
        access_url.appendChild(doc.createCDATASection(url))
        permissions_meta = doc.createElement("nstl_ors:permissions_meta")
        access_meta.appendChild(permissions_meta)
        copyright_statement = doc.createElement("nstl_ors:copyright-statement")
        if copyright_text != "":
            copyright_text = "no copyright"
        permissions_meta.appendChild(copyright_statement)
        copyright_statement.appendChild(doc.createCDATASection(copyright_text))
        license = doc.createElement("nstl_ors:license")
        permissions_meta.appendChild(license)
        #TODO 通过检查的没加这个
        #license.setAttribute("license-type", journal_meta['license_type'])
        license.setAttribute("xlink:href", xlink)
        license.appendChild(doc.createCDATASection(license_text))
        available_time = doc.createElement("nstl_ors:available_time")
        #TODO
        #permissions_meta.appendChild(available_time)
        available_time.appendChild(doc.createTextNode(journal_meta['available_time']))
        oa_type = doc.createElement("nstl_ors:OA-type")
        #permissions_meta.appendChild(oa_type)
        #TODO
        #oa_type.appendChild(doc.createTextNode(journal_meta['oa_type']))

        #TODO what's this?
        related_object_group = doc.createElement("nstl_ors:related_object_group")
        work_meta.appendChild(related_object_group)
        related_object = doc.createElement("nstl_ors:related_object")
        related_object_group.appendChild(related_object)
        ro_id = doc.createElement("nstl_ors:ro_id")
        related_object.appendChild(ro_id)
        #TODO PDF的ID和Article的ID取一样的，其他需求可能不适用
        ro_id.appendChild(doc.createTextNode(pdf_name))
        ro_title = doc.createElement("nstl_ors:ro_title")
        related_object.appendChild(ro_title)
        ro_title.appendChild(doc.createTextNode(pdf_name + ".pdf"))
        ro_type = doc.createElement("nstl_ors:ro_type")
        #TODO
        #related_object.appendChild(ro_type)
        ro_type.appendChild(doc.createTextNode("CompleteContent"))
        media_type = doc.createElement("nstl_ors:media_type")
        related_object.appendChild(media_type)
        media_type.appendChild(doc.createTextNode("PDF"))
        ro_self_url = doc.createElement("nstl_ors:self-uri") 
        related_object.appendChild(ro_self_url)
        ro_self_url.setAttribute("content-type", "PDF")
        ro_self_url.setAttribute("xlink:href", pdf_file_path)  
        ro_access_meta = doc.createElement("nstl_ors:access_meta")
        related_object.appendChild(ro_access_meta)
        ro_access_url = doc.createElement("nstl_ors:access_url")
        ro_access_meta.appendChild(ro_access_url)
        ro_access_url.appendChild(doc.createCDATASection(pdf_link))

        management_meta = doc.createElement("nstl_ors:management-meta")
        work_meta.appendChild(management_meta)
        creator = doc.createElement("nstl_ors:creator")
        management_meta.appendChild(creator)
        creator.appendChild(doc.createTextNode("NK"))
        create_time = doc.createElement("nstl_ors:create_time")
        management_meta.appendChild(create_time)
        create_time.appendChild(doc.createTextNode("%s" % self.now))
        revision_time = doc.createElement("nstl_ors:revision_time")
        #TODO
        #management_meta.appendChild(revision_time)
        revision_time.appendChild(doc.createTextNode("%s" % self.now))

        xml_str = doc.toprettyxml(indent="  ").encode('utf-8')
        with open(xml_file_path, "w") as f:
            f.write(xml_str)

        pdf_dir = "C:\Users\hp\Desktop\%s" % pdf_file_path.replace("/", "\\").replace(".\\xml_result\\", "xml_result")

        #print "%s,%s,%s" %(pdf_dir, pdf_link, doi)
        output_meta['collection_id'] = journal_meta['collection_id'] #期刊ID
        output_meta['source_id'] = journal_meta['source_id'] #平台ID
        output_meta['system_id'] = journal_meta['system_id'] #加工号?
        output_meta['ro_id'] = pdf_name
        output_meta['work_id'] = article_id
        output_meta['doi'] = doi
        output_meta['work_title'] = title
        output_meta['issn'] = journal_meta['issn']
        output_meta['eissn'] = journal_meta['eissn']
        output_meta['collection_title'] = journal_name
        output_meta['platform_url'] = journal_meta['platform_url']
        output_meta['source_name'] = 'Molecular Diversity Preservation International'
        output_meta['keywords'] = keywords
        output_meta['language'] = 'eng'
        output_meta['abstract'] = abstract
        output_meta['country'] = journal_meta['country']
        output_meta['publish_year'] = date
        output_meta['publish_date'] = publish_date
        output_meta['volume'] = volume
        output_meta['issue'] = issue
        output_meta['access_url'] = url
        output_meta['license_text'] = license_text
        output_meta['license_url'] = xlink
        output_meta['copyright'] = copyright_text
        output_meta['ro_title'] = pdf_name + ".pdf"
        output_meta['xml_uri'] = xml_file_path
        output_meta['pdf_uri'] = pdf_file_path
        output_meta['pdf_access_url'] = pdf_link
        output_meta['creator'] = 'NK'
        output_meta['create_time'] = self.now
        self.save_article_info(output_meta)
        #self.output_meta_file.write(json.dumps(output_meta))
        #self.output_meta_file.write('\n')

    """
    Save article info to mysql, update when row exists
    """
    def save_article_info(self, article_info):
        self.mysql_helper.insert(self.article_table, article_info)
    """
    Save article author info to mysql, update when row exists
    """
    def save_article_author_info(self, article_author_info):
        self.mysql_helper.insert(self.author_table, article_author_info)

    def load_journal_meta(self, all_journal_meta_xls):
        """
        Load all journal meta info from xls file
        """
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
            if journal in self.all_journal_meta:
               raise Exception("journal find multiple meta info: %s" % journal)

            print "load journal :%s" % journal.encode("utf-8")

            self.all_journal_meta[journal] = {
            'journal_id': rowValues[0],
            'issn': rowValues[1],
            'eissn': rowValues[2],
            'country': rowValues[5],
            'language': rowValues[6], 'license_type': rowValues[17], 'license_text': rowValues[18], 'oa_type': rowValues[19], 
            'available_time': rowValues[20],
            'platform_url': rowValues[27], 'system_id': rowValues[40],
            'collection_id': rowValues[43], 'source_id': rowValues[44]}

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
        article_id = "JA%s%07dNK" % (self.today, self.next_article_id)
        self.next_article_id = self.next_article_id + 1
        return article_id

    def get_article_field(self, article_info, field, convert = True, throw_exception = True):
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
        return ret

if __name__ == "__main__":
    journal_meta = sys.argv[1]
    input_filename = sys.argv[2]
    save_path = sys.argv[3]

    json2xml = Json2Xml(journal_meta, input_filename, save_path)
    #json2xml.convert()
    json2xml.convert_from_database()
