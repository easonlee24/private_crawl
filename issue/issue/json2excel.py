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
    for index in range(1, len(dataList)):
        for i in range(0, len(row0)):
            sheet1.write(index, i, dataList[index][i], default)
    f.save(path)


if __name__ == '__main__':

    row0 = []
    print linecache.getline(filename, 1)
    jsondic= json.loads(linecache.getline(filename, 1))
    for k in jsondic:
        row0.append(k)
    # row0 = [u"country", u"topic", u"resultNum", u"issue_type", u"title", u"chapter_authors_editors", u"authors_editors",
    #         u"published", u"pages", u"vol", u"no", u"doi", u"booktitle", u"book_isbn", u"book_eisbn", u"issn",
    #         u"book_doi",
    #         u"abstract", u"related_regions", u"related_countries", u"related_topics", u"keywords", u"pdf_links",
    #         u"epub_links",
    #         u"from"]
    dataList = []
    with open(filename, 'rb') as fp:
        for line in fp:
            try:
                json_date = json.loads(line)
            except Exception as e:
                pass
            data = []
            for k in row0:
                column_data = json_date.get(k, "")
                if type(column_data) is list:
                    column_data = "".join(filter(None, column_data))
                data.append(column_data)
            dataList.append(data)
    write_excel(dataList, row0, savepath)
