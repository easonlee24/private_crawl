#!/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import re
from datetime import datetime

class MergeMeta(object):
    def __init__(self, origin_meta_file, sup_meta_file):
        self.origin_meta_file = origin_meta_file
        self.sup_meta_file = sup_meta_file

    def merge(self):
        sup_meta_dict = {}
        with open(self.sup_meta_file) as f:
            for line in f:
                try:
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    continue
                url = json_data['access_url']
                sup_meta_dict[url] = json_data

        with open(self.origin_meta_file) as f:
            for line in f:
                try:
                    line = line.strip()
                    json_data = json.loads(line)
                except Exception as e:
                    continue

                try: 
                    url = json_data['url']
                except Exception as e:
                    url = json_data['access_url']
                    
                if url not in sup_meta_dict:
                    print json.dumps(json_data)
                    continue

                sup_data = sup_meta_dict[url]

                if "authors" in json_data and json_data["authors"]!= "":
                    continue

                json_data["authors"] = sup_data["authors"]

                print json.dumps(json_data)

    def convert_publish_date(self, origin_publish_date):
        #print origin_publish_date
        publish_date = re.sub(r'[^\x00-\x7f]', ' ', origin_publish_date)
        elems = re.split(',|\.|/| ', publish_date)
        elems = filter(None, elems)

        year = elems[-1]
        month_dict = {'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'June' : 6, 'July' : 7, 'Aug': 8, 'Sept' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12}
        #error_month_dict = {'Paulo', 'Janeiro', 'polis', 'Alegre', 'Dez'}
        error_month_dict = {}
        if elems[-2].isdigit():
            day = elems[-2]
            month = elems[-3]
            if month in month_dict:
                month = month_dict[month]
                publish_date = "%s-%s-%s" % (year, month, day)
            else:
                publish_date = year
        else:
            month = elems[-2]
            if month in month_dict:
                month = month_dict[month]
                publish_date = "%s-%s" % (year, month)
            else:
                publish_date = year
        
        #date = datetime.strptime("%s-%s-%s" % (month, day, year), "%b-%d-%Y")
        #publish_date = date.strftime("%Y-%m-%d")
        return publish_date

if __name__ == '__main__':
    origin_meta_file = sys.argv[1]
    sup_meta_file = sys.argv[2]
    merge_meta = MergeMeta(origin_meta_file, sup_meta_file)
    merge_meta.merge()
