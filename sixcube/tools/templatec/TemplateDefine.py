#!/usr/bin/env python
# coding: utf-8

import re
from xml.etree import ElementTree


class TemplateDefine:
    '''
    TempalateDefine可以读取一个XML数据模板文件的格式定义
    '''

    def __init__(self, xml_path):
        f = file(xml_path, 'r')
        self.tree = ElementTree.ElementTree(file=f)
        self.root = self.tree.getroot()

    def get_class_name(self):
        return self.root.tag.strip()

    def get_fields(self):
        return self.root

    def get_ftype(self, field):
        if field.attrib.has_key('type'):
            ftype = field.attrib['type'].strip()
            if ftype == "uint":
                return "uint32"
            elif ftype == "int":
                return "int32"
            elif ftype == "float":
                return "float32"
            else:
                return ftype

        else:
            return 'type_not_defined'

    def get_fcomment(self, field):
        if field.attrib.has_key('comment'):
            return field.attrib['comment'].strip()
        else:
            return ''

    def get_skeleton(self):
        if self.root.attrib.has_key('skeleton'):
            return self.root.attrib['skeleton'].strip()
        else:
            return ''

    def get_key(self, isLower=False):
        if self.root.attrib.has_key('key'):
            key = self.root.attrib['key'].strip()
            kname = re.findall('([A-Z][\w-]*)', key)[0]

            if isLower:
                if kname.lower() == "type":
                    kname = kname + "_"
                return kname.lower()
            else:
                return kname
        else:
            return '_key_not_defined_'

    def get_key_type(self):
        if self.root.attrib.has_key('key'):
            key = self.root.attrib['key'].strip()
            for field in self.root:
                if self.get_fname(field) == key:
                    return self.get_ftype(field)
        else:
            return '_key_not_defined_'

    def get_subkey(self, isLower=False):
        if self.root.attrib.has_key('sub'):
            sub = self.root.attrib['sub'].strip()
            subname = re.findall('([A-Z][\w-]*)', sub)[0]
            if isLower:
                if subname.lower() == "type":
                    subname = subname + "_"
                return subname.lower()
            else:
                return subname
        else:
            return '_sub_not_defined_'

    def get_sub_type(self):
        if self.root.attrib.has_key('sub'):
            key = self.root.attrib['sub'].strip()
            for field in self.root:
                if self.get_fname(field) == key:
                    return self.get_ftype(field)
        else:
            return '_sub_not_defined_'

    def get_fname(self, field, remove_prefix=False):
        if field.attrib.has_key('field'):
            f_text = field.attrib['field'].strip()
            if remove_prefix:
                return re.findall('([A-Z][\w-]*)', f_text)[0]
            else:
                return f_text
        else:
            return 'type_not_defined'


if __name__ == '__main__':
    xmldef = TemplateDefine("../defines/11050401_NpcTemplate.xml")
    print xmldef.get_class_name()