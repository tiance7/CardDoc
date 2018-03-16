#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys, os, re, optparse

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'SchemaObject.zip'))

import schemaobject
from mako.template import Template


class SqlFormatter:
    def __init__(self, table):
        self.table = table

    def underscore_to_camelcase(self, value):
        def camelcase():
            # yield str.lower
            while True:
                yield str.capitalize

        c = camelcase()
        return "".join(c.next()(x) if x else '_' for x in value.split("_"))

    def get_table_type(self, tableName, prefix):

        if len(options.prefix) > 0 and tableName.find(options.prefix) == 0:
            ttype = tableName.replace(options.prefix, "")
        else:
            ttype = tableName

        if ttype[-1] == 's' and ttype[-6:] != 'status':
            return ttype[:-1]
        else:
            return ttype

    def get_type_name(self, tableName, prefix):

        if tableName[-1] == 's' and tableName[-6:] != 'status':
            tableName = tableName[:-1]

        if len(options.prefix) > 0 and tableName.find(options.prefix) == 0:
            tname = tableName.replace(options.prefix, "")
        else:
            tname = tableName

        return self.underscore_to_camelcase(tname)

    def get_col_name(self, col):
        return self.underscore_to_camelcase(col.name)

    def get_col_tag(self, col):
        tag = '`gorm:"column:' + col.name
        if col.key == 'PRI' or col.extra == 'auto_increment':
            if col.name.lower() != "id":
                tag += ';primary_key'

        tag += '" sql:"type:' + self.get_col_sql_type(col) + ' ' + col.extra + ';'
        if col.null == False:
            tag += "not null;"

        if col.default is not None:
            if col.type.find('char') == 0 or \
                            col.type.find('varchar') == 0 or \
                            col.type.find('text') == 0 or \
                            col.type.find('mediumtext') == 0 or \
                            col.type.find('longtext') == 0:
                tag += 'default:"' + col.default + '";'
            else:
                tag += 'default:' + col.default + ';'

        tag += self.get_col_size(col)
        tag += self.get_index_tag(col)

        return tag + '"`'

    def get_index_tag(self, col):
        tag = ""
        for index_name in self.table.indexes:
            index = self.table.indexes[index_name]
            for f in index.fields:
                if f[0] == col.name and not 'PRIMARY' == index_name:
                    if index.non_unique:
                        tag += "index:%s;" % index_name
                    else:
                        tag += "unique_index:%s;" % index_name
        return tag

    def get_col_sql_type(self, col):
        index = col.type.find('(')
        if index == -1:
            return col.type
        else:
            return col.type[:index]

    def get_col_type(self, col):
        if col.type.find('int') == 0 or col.type.find('mediumint') == 0:
            if col.null:
                return "sql.NullInt64"
            elif (col.type.find('unsigned') > 0):
                return 'uint32'
            else:
                return 'int32'
        elif col.type.find('bigint') == 0:
            if col.null:
                return "sql.NullInt64"
            elif (col.type.find('unsigned') > 0):
                return 'uint64'
            else:
                return 'int64'
        elif col.type.find('small') == 0:
            if col.null:
                return "sql.NullInt64"
            elif (col.type.find('unsigned') > 0):
                return 'uint16'
            else:
                return 'int16'
        elif col.type.find('tiny') == 0 or col.type.find('enum') == 0:
            if col.null:
                return "sql.NullInt64"
            elif (col.type.find('unsigned') > 0):
                return 'uint8'
            else:
                return 'int8'
        elif col.type.find('char') == 0 or \
                        col.type.find('varchar') == 0 or \
                        col.type.find('text') == 0 or \
                        col.type.find('mediumtext') == 0 or \
                        col.type.find('longtext') == 0:
            if col.null:
                return "sql.NullString"
            else:
                return 'string'
        elif col.type.find('float') == 0 or \
                        col.type.find('double') == 0 or \
                        col.type.find('decimal') == 0:
            if col.null:
                return "sql.NullFloat64"
            else:
                return 'float32'
        elif col.type.find('datetime') == 0 or col.type.find('date') == 0 or col.type.find('timestamp') == 0:
            return 'time.Time'
        elif col.type.find('blob') == 0 or col.type.find('varbinary') == 0 \
                or col.type.find('binary') == 0 or col.type.find('mediumblob') == 0:
            return '[]byte'
        else:
            print "unkown column type:", col.type
            return 'None'

    def get_col_size(self, col):
        if col.type.find('varchar') == 0 or col.type.find('char') == 0:
            return 'size:%d;' % (int(re.compile("\((.*)\)").search(col.type).group(1)) + 1)
        # elif col.type.find('datetime') == 0:
        #     return ';size:20'
        # elif col.type.find('date') == 0:
        #     return ' column_size="11" '
        # elif col.type.find('text') == 0:
        #     return ' column_size="256" '
        else:
            return ''

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

    def get_imports(self, columns):
        imps = set()
        for col in columns:
            if self.get_col_type(columns[col]).find('sql.') == 0:
                imps.add("database/sql")
            elif self.get_col_type(columns[col]).find('time.') == 0:
                imps.add("time")
        return imps


if __name__ == '__main__':

    parser = optparse.OptionParser(
        usage="usage: %s -d mysql://username:password@host:port/database [-o output] " % os.path.basename(sys.argv[0]))
    parser.add_option("-d", "--database", action="store", dest="database", default="",
                      help="database to generate the gorm define")
    parser.add_option("-o", "--output", action="store", dest="output", default="gorm_out",
                      help="output directory")
    parser.add_option("-p", "--package", action="store", dest="package", default="models",
                      help="go source package")
    parser.add_option("-r", "--prefix", action="store", dest="prefix", default="",
                      help="table prefix")

    (options, args) = parser.parse_args()

    if options.database is None or "" == options.database:
        print >> sys.stderr, "A database must be specified!"
        parser.print_help()
        sys.exit(1)

    if options.output is None or "" == options.output:
        options.output = "qb_out"

    if not os.path.exists(options.output):
        os.mkdir(options.output)

    try:
        schema = schemaobject.SchemaObject(options.database)
    except:
        print "Unexpected error:", sys.exc_info()[1]
        sys.exit()

    template = Template(filename="templates/qb_define_go.mako")

    for database in schema.databases:
        for tableName in schema.databases[database].tables:
            print "%s.%s....." % (database, tableName),

            table = schema.databases[database].tables[tableName]

            formatter = SqlFormatter(table)

            output = file(os.path.join(options.output, '%s.go' % formatter.get_table_type(tableName, options.prefix)),
                          'w')

            xmlStr = template.render_unicode(
                className="%s" % formatter.underscore_to_camelcase(tableName),
                package=options.package,
                typeName=formatter.get_type_name(tableName, options.prefix),
                f=formatter,
                tableName=tableName,
                columns=schema.databases[database].tables[tableName].columns,
                imps=formatter.get_imports(schema.databases[database].tables[tableName].columns),
            ).encode('utf-8')

            output.write(
                xmlStr
            )
            print " done."
