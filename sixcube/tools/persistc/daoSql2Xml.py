#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys, os, re

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'SchemaObject.zip'))

import schemaobject
from xml.etree import ElementTree
from mako.runtime import Context
from mako.template import Template


class SqlFormatter:
    def underscore_to_camelcase(self, value):
        def camelcase():
            #yield str.lower
            while True:
                yield str.capitalize

        c = camelcase()
        return "".join(c.next()(x) if x else '_' for x in value.split("_"))

    def getStructName(self, col):
        return "%s%s" % (self.getStructPrefix(col), self.underscore_to_camelcase(col.name))

    def getStructPrefix(self, col):
        return ''
        # if col.type.find('int') == 0 or col.type.find('bigint') == 0 or col.type.find('small') == 0 or col.type.find('tiny') == 0:
        #     return 'n'
        # elif col.type.find('char') == 0 or col.type.find('varchar') == 0 or col.type.find('text') == 0:
        #     return 'sz'
        # elif col.type.find('datetime') == 0 or col.type.find('date') == 0:
        #     return 'dt'
        # elif col.type.find('float') == 0 or col.type.find('double') == 0:
        #     return 'f'


    def getColType(self, col):
        if col.type.find('int') == 0 or col.type.find('mediumint') == 0:
            if (col.type.find('unsigned') > 0):
                return 'UINT32'
            else:
                return 'INT32'
        elif col.type.find('bigint') == 0:
            if (col.type.find('unsigned') > 0):
                return 'UINT64'
            else:
                return 'INT64'
        elif col.type.find('small') == 0:
            if (col.type.find('unsigned') > 0):
                return 'UINT16'
            else:
                return 'INT16'
        elif col.type.find('tiny') == 0:
            if (col.type.find('unsigned') > 0):
                return 'UINT8'
            else:
                return 'INT8'
        elif col.type.find('char') == 0 or \
                        col.type.find('varchar') == 0 or \
                        col.type.find('text') == 0 or \
                col.type.find('mediumtext') == 0 or \
                col.type.find('longtext') == 0 :
            return 'char'
        elif col.type.find('float') == 0 or \
                        col.type.find('double') == 0 or \
                col.type.find('decimal') == 0:
            return 'FLOAT'
        elif col.type.find('datetime') == 0 or col.type.find('date') == 0:
            return 'char'
        else:
            print "unkown column type:", col.type
            return 'None'

    def getColSize(self, col):
        if col.type.find('varchar') == 0 or col.type.find('char') == 0:
            return ' column_size="%d" ' % (int(re.compile("\((.*)\)").search(col.type).group(1)) + 1)
        elif col.type.find('datetime') == 0:
            return ' column_size="20" '
        elif col.type.find('date') == 0:
            return ' column_size="11" '
        elif col.type.find('text') == 0:
            return ' column_size="256" '
        else:
            return ' '

    def getAutoIncrement(self, col):
        if col.extra == 'auto_increment':
            return ' auto_increment="true" '
        else:
            return ' '

    def getIndexType(self, idx):
        if idx.name == 'PRIMARY':
            return 'primary'
        elif idx.non_unique:
            return 'index'
        else:
            return 'unique'

    def getIndexFields(self, idx):
        return ','.join([x[0] for x in idx.fields])


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: %s mysql://username:password@host:port/database" % os.path.basename(sys.argv[0])
        sys.exit()

    try:
        schema = schemaobject.SchemaObject(sys.argv[1])
    except:
        print "Unexpected error:", sys.exc_info()[1]
        sys.exit()

    template = Template(filename="templates/define.xml.mako")
    formatter = SqlFormatter()

    for database in schema.databases:
        for tableName in schema.databases[database].tables:
            print "%s.%s....." % (database, tableName),
            output = file(os.path.join('output', '%s.xml' % tableName), 'w')

            xmlStr = template.render_unicode(
                className="%s" % formatter.underscore_to_camelcase(tableName),
                tableName=tableName,
                rawType=tableName.upper(),
                f=formatter,
                columns=schema.databases[database].tables[tableName].columns,
                indexes=schema.databases[database].tables[tableName].indexes
            ).encode('utf-8')

            output.write(
                xmlStr
            )
            print " done."