# coding: utf-8
# #!/usr/bin/env python
import os.path, sys
from persistConsts import *
from inflection import *
from xml.etree import ElementTree

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))

from mako.runtime import Context
from mako.template import Template

from DaoObjectDef import DaoObjectDef

tools_dir = os.path.dirname(os.path.realpath(__file__))


class DaoContainerDef:
    def __init__(self, def_path, file_name, prefix):

        # 加载并解析容器类的定义文件
        def_file = os.path.join(def_path, file_name)
        self.root = ElementTree.ElementTree(file=file(def_file, 'r')).getroot()

        # 加载并解析子容器类的定义文件
        f = file(os.path.join(def_path, self.get_element_file()), 'r')
        self.tree = ElementTree.ElementTree(file=f)
        self.elementDef = DaoObjectDef(self.tree.getroot())

        # 其他的辅助字段
        self.refKeys = []
        self.idxKeys = []
        self.fRdr = FieldReader()
        self.prefix = prefix


    def get_classname(self):
        return self.tree.getroot().tag.strip()

    def get_raw_type(self):
        return self.root.find('raw_type').text.strip().upper()

    def get_module(self):
        return self.root.attrib['module'].strip().upper().replace('/', '_')

    def get_module_path(self):
        return "%s" % self.root.attrib['module'].strip()

    def get_package(self):
        mpath = "%s" % self.root.attrib['module'].strip()
        return os.path.basename(mpath[:-1])

    # 获取map的下标的索引字段
    def get_index_fields_string(self):
        if not self.root.find(".//idx_key") is None:
            return self.root.find(".//idx_key").text.strip()
        else:
            return ''
            
    def get_index_signature(self):
        signatures = []
        self.get_index_fields()
        for field in self.idxKeys:
            signatures.append("%s %s" % (self.fRdr.getCType(field), self.fRdr.getName(field)))
        return ', '.join(signatures)

    def hasRowLimit(self):
        if self.root.find('set_limit') is None:
            return False

        return self.root.find('set_limit').text.strip() == 'true'

    # 用作MAP的索引的字段
    def get_index_fields(self):
        if len(self.idxKeys) == 0:
            self.idxKeys = self.elementDef.get_ref_fields(self.get_index_fields_string())
        
        return self.idxKeys

    def get_element_file(self):
        if not self.root.find(".//element_def") is None:
            return self.root.find(".//element_def").text.strip()
        else:
            return ''

    def get_skeleton(self):
        return self.root.attrib['skeleton'].strip()

    def get_element_class(self):
        if not self.root.find(".//class_name") is None:
            return self.root.find(".//class_name").text.strip()
            
        if 'DaoArray' == self.get_skeleton():
            return "%sArray" % self.get_element_define().get_classname()
        elif 'DaoMap' == self.get_skeleton():
            return "%sMap" % self.get_element_define().get_classname()
        elif 'DaoHashMap' == self.get_skeleton():
            return "%sHash" % self.get_element_define().get_classname()

    def get_element_define(self):
        return self.elementDef

    def get_object_type(self):
        if 'object_type' in self.root.attrib:
            return self.root.attrib['object_type'].strip()
        else:
            return "object_type_IS_NOT_DEFINED"

    def get_ref_key_string(self):
        if not self.root.find(".//ref_keys") is None:
            return self.root.find(".//ref_keys").text.strip()
        else:
            return ''

    def get_ref_signature(self):
        signatures = []
        self.get_ref_keys()
        for field in self.refKeys:
            signatures.append("%s %s" % (self.fRdr.getCType(field), self.fRdr.getName(field)))
        return ', '.join(signatures)

    def get_ref_keys(self):
        if len(self.refKeys) == 0:
            self.refKeys = self.elementDef.get_ref_fields(self.get_ref_key_string())
        return self.refKeys
        
    def has_ref_in_key(self):
        if not self.root.find(".//ref_in_key") is None:
            return True
            
        return False
        
    def get_ref_in_key(self):
        return self.root.find(".//ref_in_key")
        
    def get_ref_in_key_size(self):
        return int(self.get_ref_in_key().attrib['column_size'])

    def get_where_clause(self, as_stmt):
        if not self.root.find(".//ref_where") is None:
            return self.root.find(".//ref_where").text.strip()

        clause = []
        for key in self.get_ref_keys():
            clause.append('%s=%s' % (key.attrib['column_name'].strip(),
                                     self.elementDef.get_column_place_holder(key, SQL_OP_SELECT, as_stmt))
                          )
        
        if self.has_ref_in_key():
            inKey = self.get_ref_in_key()
            inStr = ','.join(['?'] * int(inKey.attrib['column_size']))
            clause.append('%s in (%s)' % (inKey.attrib['column_name'].strip(),
                                          inStr))
        
        if len(clause) > 0:
            return ' AND '.join(clause)
        else:
            return '1'

    # 生成C++的代码
    def generate_cpp(self, out_dir):

        skeleton = self.get_skeleton()

        if skeleton in ["DaoMap", "DaoHashMap"]:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleMap_h.mako'))
        else:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleArray_h.mako'))

        output = file('%s/%s%s.h' % (out_dir, self.get_module_path(), self.get_element_class()), 'w')
        output.write(
            template.render_unicode(
                container=self,
                element=self.elementDef,
                refKeys=self.get_ref_keys(),
                refInKey=self.get_ref_in_key(),
                fRdr=FieldReader(),
                mapKey=self.get_index_fields(),
                METHOD=GO_2_METHOD,
                PREFIX=self.prefix,
                PACKAGE=os.path.basename(self.prefix)
            ).encode('gb2312')
        )

        if skeleton in ["DaoMap", "DaoHashMap"]:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleMap_cpp.mako'))
        else:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleArray_cpp.mako'))

        output = file('%s/%s%s.cpp' % (out_dir, self.get_module_path(), self.get_element_class()), 'w')
        output.write(
            template.render_unicode(
                container=self,
                element=self.elementDef,
                refKeys=self.get_ref_keys(),
                refInKey=self.get_ref_in_key(),
                fRdr=FieldReader(),
                mapKey=self.get_index_fields(),
                METHOD=GO_2_METHOD,
                PREFIX=self.prefix,
                PACKAGE=os.path.basename(self.prefix)
            ).encode('gb2312')
        )

    # 生成Golang的代码
    def generate_go(self, out_dir):

        skeleton = self.get_skeleton()

        if skeleton in ["DaoMap", "DaoHashMap"]:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleMap_go.mako'))
        else:
            template = Template(filename=os.path.join(tools_dir, 'templates/SampleArray_go.mako'))

        output = file('%s.go' % os.path.join(out_dir, underscore(self.get_element_class())), 'w')
        output.write(
            template.render_unicode(
                container=self,
                element=self.elementDef,
                refKeys=self.get_ref_keys(),
                fRdr=FieldReader(),
                mapKey=self.get_index_fields(),
                METHOD=GO_2_METHOD,
                PACKAGE=os.path.basename(self.prefix)
            ).encode('utf-8')
        )


if __name__ == '__main__':
    define = DaoContainerDef('dao_map.xml')

    print define.get_ref_key_string()

    elementDef = define.get_element_define()

    print elementDef.get_table_name(), define.get_index_fields()

    define.generate_cpp()