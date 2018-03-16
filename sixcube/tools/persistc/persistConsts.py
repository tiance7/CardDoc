# coding: utf-8
# #!/usr/bin/env python

import re
import time
from xml.etree import ElementTree as tree

SQL_OP_SELECT = 1
SQL_OP_INSERT = 2
SQL_OP_UPDATE = 3
SQL_OP_DELETE = 4
SQL_OP_INSERT_DUPLICATE_UPDATE = 5

# Declare the DataObject access signature
DATATYPE_2_SIGNATURE = {
    'UINT32': 'UInt32',
    'UINT64': 'UInt64',
    'UINT16': 'UInt16',
    'UINT8': 'UInt8',
    'INT32': 'Int32',
    'INT64': 'Int64',
    'INT16': 'Int16',
    'char': 'String',
    'FLOAT': 'Float',
    'INT8': 'Int8',
    'blob' : 'Blob'
}

# Declare to MySQL column type
DATATYPE_2_MYSQL = {
    'UINT32': 'INT UNSIGNED',
    'UINT64': 'BIGINT UNSIGNED',
    'UINT16': 'SMALLINT UNSIGNED',
    'UINT8': 'TINYINT UNSIGNED',
    'INT32': 'INT',
    'INT64': 'BIGINT',
    'INT16': 'SMALLINT',
    'INT8': 'TINYINT',
    'char': 'VARCHAR',
    'FLOAT': 'FLOAT',
    'datetime': 'DATETIME',
    'blob' : 'BLOB'
}

# Declare to MySQL column type
DATATYPE_2_MYSQL_DEFAULT = {
    'UINT32': '0',
    'UINT64': '0',
    'UINT16': '0',
    'UINT8': '0',
    'INT32': '0',
    'INT64': '0',
    'INT16': '0',
    'INT8': '0',
    'char': '',
    'FLOAT': '0',
    'blob' : ''
}

DATATYPE_2_PLACEHOLDER = {
    'UINT32': '%u',
    'UINT64': '%llu',
    'UINT16': '%u',
    'UINT8': '%u',
    'INT32': '%d',
    'INT64': '%d',
    'INT16': '%d',
    'INT8': '%d',
    'char': "'%s'",
    'FLOAT': '%.3f',
    'blob' : "'%s'"
}

DATATYPE_2_CLANG = {
    'UINT32': 'UINT32',
    'UINT64': 'UINT64',
    'INT32': 'INT32',
    'INT64': 'INT64',
    'INT16': 'INT16',
    'UINT16': 'UINT16',
    'char': 'const char*',
    'FLOAT': 'FLOAT',
    'UINT8': 'UINT8',
    'INT8': 'INT8',
    'blob': 'const char*',
}

DATATYPE_2_GOLANG = {
    'UINT32': 'uint32',
    'UINT64': 'uint64',
    'INT32': 'int32',
    'INT64': 'int64',
    'INT16': 'int16',
    'UINT16': 'uint16',
    'char': 'string',
    'FLOAT': 'float32',
    'UINT8': 'uint8',
    'INT8': 'int8',
    'blob': 'string'
}

DATATYPE_2_GO_SIGNATURE = {
    'UINT32': 'Uint32',
    'UINT64': 'Uint64',
    'UINT16': 'Uint16',
    'UINT8': 'Uint8',
    'INT32': 'Int32',
    'INT64': 'Int64',
    'INT16': 'Int16',
    'char': 'String',
    'FLOAT': 'Float',
    'INT8': 'Int8',
    'blob': 'Blob'
}

DATATYPE_2_TYPESIZE = {
    'UINT32': '4',
    'UINT64': '8',
    'UINT16': '2',
    'UINT8': '1',
    'INT32': '4',
    'INT64': '8',
    'INT16': '2',
    'char': '1',
    'FLOAT': '4',
    'INT8': '1',
    'blob': '1',
}

GO_2_METHOD = {
    "int": "Int32",
    "int8": "Int8",
    "int16": "Int16",
    "int32": "Int32",
    "int64": "Int64",
    "uint": "Uint32",
    "uint8": "Uint8",
    "uint16": "Uint16",
    "uint32": "Uint32",
    "uint64": "Uint64",
    "string": "String",
    "float": "float32",
    "float32": "float32",
    "bool": "Uint8",
}


class FieldReader:
    def getName(self, field, remove_prefix=False):
        if remove_prefix:
            name = re.findall('([A-Z][\w-]*)', field.text.strip())[0]
        else:
            name = field.text.strip()

        if 'Type' == name:
            return 'Type_'
        else:
            return name

    def getTimeString(self):
        return time.strftime('%Y-%m-%d %X', time.localtime())

    def isAutoIncrement(self, field):
        return not field.find('[@auto_increment="true"]') is None

    def isString(self, field):
        if not field.find('[@data_type="datetime"]') is None:
            return True
        elif not field.find('[@data_type="blob"]') is None:
            return True
        
        return not field.find('[@data_type="char"]') is None
        
    def isBlob(self, field):
        return not field.find('[@data_type="blob"]') is None
    
    def isMysqlString(self, field):
        return not field.find('[@data_type="char"]') is None

    def hasInsertVal(self, field):
        return field.attrib.has_key('insert_val')

    def getInsertVal(self, field):
        return field.attrib.get('insert_val', '--').strip()

    def hasUpdateVal(self, field):
        return field.attrib.has_key('update_val')

    def getUpdateVal(self, field):
        return field.attrib.get('update_val', '--').strip()

    def isIgnoreOnUpdate(self, field):
        return field.attrib.has_key('ignore_on_update')
    
    def isDuplicateKeyUpdate(self, field):
        return field.attrib.has_key('duplicate_key_update')
    
    def getType(self, field):
        if field.attrib.has_key('data_type'):
            dataType = field.attrib['data_type'].strip()
            if dataType == "datetime" or dataType == "blob":
                return "char"
            return dataType
        else:
            return 'data_type_not_defined'

    def getMapIndexType(self, fields):
        if len(fields) == 1:
            return self.getKeyType(fields[0])
        elif len(fields) == 2:
            if self.getKeyType(fields[0]) == "std::string" or self.getKeyType(fields[0]) == "std::string" :
                return "std::string"
            return "UINT64"  #只支持两个字段组合成主键
        else:
            return "_INVALID_"

    def getKeyType(self, field):
        if field.attrib.has_key('data_type'):
            dataType = field.attrib['data_type'].strip()
            if dataType == "char":
                return "std::string"
            return dataType
        else:
            return 'data_type_not_defined'

    def getTypeSize(self, field):
        if field.attrib['data_type'].strip() == "datetime":
            return '32' + " + 2"
        elif field.attrib.has_key('column_size'):
            return field.attrib['column_size'].strip() + " + 2"
        else:
            return DATATYPE_2_TYPESIZE[self.getType(field)]

    def getLength(self, fields):
        return '+'.join([self.getTypeSize(f) for f in fields])

    def getSize(self, field):
        if field.attrib['data_type'].strip() == "datetime":
            return '32'
        elif field.attrib.has_key('column_size'):
            return field.attrib['column_size'].strip()
        else:
            return 'column_size_not_defined'

    def getColumn(self, field):
        if field.attrib.has_key('column_name'):
            return field.attrib['column_name'].strip()
        else:
            return 'column_name_not_defined'

    def getComment(self, field):
        if field.attrib.has_key('comment'):
            return field.attrib['comment'].strip()
        else:
            return ''

    def getMysqlNull(self, field):
        if field.attrib.has_key('null') and field.attrib['null'] == 'true':
            return 'NULL'
        else:
            return 'NOT NULL'

    def getMysqlDefault(self, field):
        data_type = field.attrib['data_type'].strip()
        if data_type == "datetime":
            return ''
        elif self.isAutoIncrement(field):
            return ''
        elif 'default' in field.attrib:
            return "DEFAULT '%s'" % field.attrib['default'].strip()
        else:
            return "DEFAULT '%s'" % DATATYPE_2_MYSQL_DEFAULT[data_type]

    def getMysqlType(self, field):
        data_type = field.attrib['data_type'].strip()
        if data_type in DATATYPE_2_MYSQL:
            return DATATYPE_2_MYSQL[data_type];
        else:
            return '__nOT_dFINED__'

    def getMysqlSize(self, field):
        if field.attrib['data_type'].strip() == "datetime":
            return '32'
        elif field.attrib.has_key('column_size'):
            return field.attrib['column_size']
        else:
            return '25'

    def getMysqlAI(self, field):
        if field.attrib.has_key('auto_increment') and field.attrib['auto_increment'].strip() == "true":
            return "AUTO_INCREMENT"
        else:
            return ''

    def getCType(self, field):
        data_type = self.getType(field)
        if data_type in DATATYPE_2_CLANG:
            return DATATYPE_2_CLANG[data_type];
        else:
            return '__nOT_dFINED__'

    def getGoType(self, field):
        data_type = self.getType(field)
        if data_type in DATATYPE_2_GOLANG:
            return DATATYPE_2_GOLANG[data_type];
        else:
            return '__nOT_dFINED__'

    def getGetMethod(self, field):
        return "Get%s()" % self.getName(field, True)

    def getSetMethod(self, field, param):
        return "Set%s(static_cast<%s>(%s))" % (
            self.getName(field, True),
            self.getCType(field),
            param
        )

    def getGetter(self, field, struct="m_data"):
        return "%s\t\t\t\tGet%s() { return %s.%s; }; " % (
            self.getCType(field),
            self.getName(field, True),
            struct,
            self.getName(field)
        )
            
    def getSetter(self, field):
        if self.isBlob(field):
            return "void \t\t\t\tSet%s(%s %s, int iLen) { if(iLen >= %s) iLen = %s - 1; memset(m_data.%s, 0, %s); memcpy(m_data.%s,%s,iLen); }; " % (
                self.getName(field, True),
                self.getCType(field),
                self.getName(field),
                self.getMysqlSize(field),
                self.getMysqlSize(field),
                self.getName(field),
                self.getMysqlSize(field),
                self.getName(field),
                self.getName(field)
            )
        elif self.isString(field):
            return "void \t\t\t\tSet%s(%s %s) { CopyString(m_data.%s,%s,%s); }; " % (
                self.getName(field, True),
                self.getCType(field),
                self.getName(field),
                self.getName(field),
                self.getName(field),
                self.getMysqlSize(field)
            )
        else:
            return "void \t\t\t\tSet%s(%s %s) { m_data.%s = %s; }; " % (
                self.getName(field, True),
                self.getCType(field),
                self.getName(field),
                self.getName(field),
                self.getName(field)
            )


class SkeletonReader:
    def __init__(self, xml_file):
        self.root = tree.ElementTree(file=file(xml_file, 'r')).getroot()

    def get_skeleton(self):
        return self.root.attrib['skeleton'].strip()