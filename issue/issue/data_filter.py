# -*- coding: utf-8 -*- 
import sys
import json

start_date = "2005"
#data_key = "date"
date_key = "release_year"
for line in sys.stdin:
    json_data = json.loads(line)
    #date may have multiple data formats:
    #1. 2017
    #2. 12 Sep 2017
    try:
        #date = " " . join(json_data[date_key])
        date = json_data[date_key]
    except KeyError as e:
        continue

    if (date < start_date):
        continue

    json_data[date_key] = date

    print json.dumps(json_data)
