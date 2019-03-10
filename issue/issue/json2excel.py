# -*- coding: utf-8 -*-
import sys
import json
import xlwt
import linecache

filename = sys.argv[1]
savepath = sys.argv[2]


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


if __name__ == '__main__':

    row0 = []
    #首先需要遍历一下所有元数据，获取到元数据中所有出现的列。在转换xls的时候，某列如果不出现在元数据中时，则此列以空字符串填充。
    with open(filename, 'rb') as fp:
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

    dataList = []
    with open(filename, 'rb') as fp:
        for line in fp:
            try:
                strlen = len(line)
                if strlen > 32672:
                    print "unexcept str len %d:" % strlen 
                    continue
                json_date = json.loads(line)
                #print "id: %s" % json_date["id"]
            except Exception as e:
                raise Exception(e)
                continue
            data = []
            for k in row0:
                column_data = json_date.get(k, "")
                if type(column_data) is list:
                    column_data = "".join(filter(None, column_data))
                data.append(column_data)
            dataList.append(data)
    write_excel(dataList, row0, savepath)
