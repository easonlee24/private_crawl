import sys
import json
import re

filename = sys.argv[1]
columnname = sys.argv[2]
split = '|'

with open(filename) as fp:
    for line in fp:
        #try:
        #    json_date = json.loads(line)
        #except Exception as e:
        #    continue
        json_date = json.loads(line)
        columns = columnname.split(",")
        line = ""
        for column in columns:
            try:
                data = json_date[column]
            except Exception as e:
                data = ""

            if type(data) is list:
                data = "".join(data)

            if column == 'url':
                data = re.sub("\?journalCode=.*", "", data)

            if isinstance(data, int):
                line += str(data) + split
            else:
                line += data.replace('\n', '').replace('\t', '').strip() + split
        print line.strip().encode('utf-8').strip(split)