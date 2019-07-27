# -*- coding: utf-8 -*- 
import sys
import json
import re
import codecs
from spiders.utils import Utils

from xml.dom import minidom
def fixed_writexml(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)
 
    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()
 
    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 \
          and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE:
            writer.write(">")
            self.childNodes[0].writexml(writer, "", "", "")
            writer.write("</%s>%s" % (self.tagName, newl))
            return
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            if node.nodeType is not minidom.Node.TEXT_NODE:
                node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))
 
minidom.Element.writexml = fixed_writexml

dom = minidom.parse("./JA201804180009617NK.xml")
node = dom.getElementsByTagName("nstl_ors:work_id")[0].childNodes[0]
node.replaceWholeText("JA201904180000001NK")
node1 = dom.getElementsByTagName("nstl_ors:self-uri")[0]
print node1.getAttribute("xlink:href")
node1.removeAttribute("xlink:href")
node1.setAttribute("xlink:href", "xml_result/JO201705230000267NK^Y2012^V1^N1/JA201904180000001NK.xml")
xml_str = dom.toprettyxml(indent="  ").encode('utf-8')
xml_file_path = "/Users/baidu/work/private_crawl/issue/issue/test1.xml"

f = codecs.open(xml_file_path,'w','utf-8')
dom.writexml(f,addindent='  ',newl='\n',encoding = 'utf-8')
#with open(xml_file_path, "w") as f:
#    f.write(xml_str)
f.close()
