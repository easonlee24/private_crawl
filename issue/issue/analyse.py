# -*- coding: utf-8 -*- 
import sys
import json
import re
from spiders.utils import Utils

filename = sys.argv[1]
columnname = sys.argv[2]
split = '|'

with open(filename) as fp:
    for line in fp:
        try:
            json_date = json.loads(line)
        except Exception as e:
            continue
        columns = columnname.split(",")
        line = ""
        for column in columns:
            try:
                data = Utils.format_value(json_date[column], join_char = '|')
            except Exception as e:
                data = ""

            if column == 'url':
                data = re.sub("\?journalCode=.*", "", data)

            if isinstance(data, int):
                line += str(data) + split
            else:
                line += data.replace('\n', '').replace('\t', '').strip() + split
        #print line.strip().replace(u'ê', 'e').replace(u'é', 'e').replace(u'ã', 'a').replace(u'ó', 'o').replace(u'ú', 'u').strip(split)
        print line.strip().strip(split)
