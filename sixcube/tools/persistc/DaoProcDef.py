# coding: utf-8
#!/usr/bin/env python

from DaoObjectDef import DaoObjectDef
from persistConsts import *
from xml.etree import ElementTree


class DaoProcDef(DaoObjectDef):
    def __init__(self, root):
        DaoObjectDef.__init__(self, root, True)
        self.returns = self.root.find('returns')

    def gen_select(self, as_stmt=False):
        field_types=[]
        for field in self.fields:
            field_types.append(self.get_column_place_holder(field, SQL_OP_INSERT, as_stmt))
        return 'CALL %s(%s)' % (
            self.get_table_name(), ','.join(field_types))


if __name__ == '__main__':
    f = file('defines/test/sp_test_5.xml', 'r')
    tree = ElementTree.ElementTree(file=f)

    procDef = DaoProcDef(tree.getroot())
    print procDef.get_object_type()