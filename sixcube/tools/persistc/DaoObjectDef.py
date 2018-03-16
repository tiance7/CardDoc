# coding: utf-8
# !/usr/bin/env python
import os.path
import string
from persistConsts import *


class DaoObjectDef:
    def __init__(self, root, is_proc=False):
        self.isProc = is_proc  # 非存储过程
        self.fRdr = FieldReader()
        self.root = root
        self.fields = self.root.find('fields')
        self.returns = self.root.find('returns')
        self.joins = self.root.find('joins')
        if self.joins == None:
            self.joins = ""


        if self.isProc:
            keys = []
        elif not self.root.find('.//indexes/index[@use_as_primary="true"]') is None:
            keys = self.root.find('.//indexes/index[@use_as_primary="true"]').text.split(",")
        elif not self.root.find('.//indexes/index[@type="primary"]') is None:
            keys = self.root.find('.//indexes/index[@type="primary"]').text.split(",")
        else:
            keys = []


        self.data_fields = []
        self.primary_fields = []
        self.ref_where_fields = []
        self.auto_fields = []
        self.getters = []
        self.setters = []

        ref_fields_keys = []
        if not self.root.find('.//ref_where_fields') is None:
            ref_fields_keys = self.root.find('.//ref_where_fields').text.split(",")
            
        for field in self.fields:
            if not self.fRdr.getColumn(field) in keys:
                self.data_fields.append(field)
            else:
                self.primary_fields.append(field)
            
            if self.fRdr.getColumn(field) in ref_fields_keys:
                self.ref_where_fields.append(field)
                
            if self.fRdr.isAutoIncrement(field):
                self.auto_fields.append(field)
            self.getters.append(self.fRdr.getGetter(field))
            self.setters.append(self.fRdr.getSetter(field))
        
        for join in self.joins:
            for child in join.getchildren():
                self.getters.append(self.fRdr.getGetter(child))
                self.setters.append(self.fRdr.getSetter(child))
            
        if len(self.primary_fields) != len(keys):
            print "ERROR:[DaoObjectDef::__init__]keys=",keys,"primary_fields=",self.primary_fields
            raise TypeError("primary fields error!")
            

    def get_skeleton(self):
        return self.root.attrib['skeleton'].strip()

    def get_classname(self):
        return self.root.tag.strip()    

    def isDynTable(self):
        return not self.root.find('[@dyn_table="true"]') is None

    def get_module(self):
        return self.root.attrib['module'].strip().upper().replace('/', '_')

    def get_module_path(self):
        return "%s" % self.root.attrib['module'].strip()

    def get_package(self):
        mpath = "%s" % self.root.attrib['module'].strip()
        return os.path.basename(mpath[:-1])

    def get_raw_type(self):
        return self.root.find('raw_type').text.strip().upper()


    def is_char_obj(self):
        if self.root.find('is_char_obj') is None:
            return False

        return self.root.find('is_char_obj').text.strip() == 'true'
        
    def has_backup_table(self):
        if self.root.find('has_backup_table') is None:
            return False

        return self.root.find('has_backup_table').text.strip() == 'true'

    def get_fields(self):
        return self.fields

    def get_joins(self):
       return self.joins     

    def get_ref_fields(self, refKeyString):
        refKeysName = refKeyString.split(',')
        refFields = []
        
        for refKeys in refKeysName:
            for field in self.fields:
                if refKeys == self.fRdr.getColumn(field):
                    refFields.append(field)
        
        return refFields

    def get_object_type(self):
        if self.root.attrib.has_key('object_type'):
            return self.root.attrib['object_type'].strip()
        else:
            return "object_type_IS_NOT_DEFINED"

    def get_signature(self, field):
        if self.fRdr.isBlob(field):
            return DATATYPE_2_SIGNATURE['blob']
        
        data_type = self.fRdr.getType(field)
        if DATATYPE_2_SIGNATURE.has_key(data_type):
            return DATATYPE_2_SIGNATURE[data_type]
        else:
            return data_type

    def get_go_signature(self, field):
        if self.fRdr.isBlob(field):
            return DATATYPE_2_GO_SIGNATURE['blob']
            
        data_type = self.fRdr.getType(field)
        if DATATYPE_2_GO_SIGNATURE.has_key(data_type):
            return DATATYPE_2_GO_SIGNATURE[data_type]
        else:
            return data_type

    def get_returns(self):
        return self.returns

    def get_uniques(self):
        return self.root.findall('.//indexes/index[@type="unique"]');

    def get_indexes(self):
        return self.root.findall('.//indexes/index[@type="index"]');

    def get_primary_columns(self):
        if self.root.find('.//indexes/index[@type="primary"]') is None:
            return ''
        else:
            return 'PRIMARY KEY(%s)' % self.root.find('.//indexes/index[@type="primary"]').text

    def get_data_fields(self):
        return self.data_fields

    def get_auto_fields(self):
        return self.auto_fields

    def get_getters(self):
        return self.getters

    def get_setters(self):
        return self.setters

    def get_primary_fields(self, is_select=False):
        if is_select and not self.root.find(".//ref_where") is None:
            return []
            
        return self.primary_fields;
        
    def get_ref_where_fields(self):
        if not self.root.find(".//ref_where") is None:
            return self.ref_where_fields
            
        return []
    
    def get_select_where_clause(self, as_stmt):
        if not self.root.find(".//ref_where") is None:
            return self.root.find(".//ref_where").text.strip()
            
        clause = []
        for key in self.primary_fields:
            column = key.attrib['column_name'].strip()
            if not self.get_alias() is None:
                column = '.'.join([self.get_alias(), column])
                
            clause.append('%s=%s' % (column,
                                     self.get_column_place_holder(key, SQL_OP_SELECT, as_stmt))
                          )
        if len(clause) > 0 :
            return ' AND '.join(clause)
        else :
            return '1'

    def get_where_clause(self, as_stmt):
        clause = []
        for key in self.primary_fields:
            clause.append('%s=%s' % (key.attrib['column_name'].strip(),
                                     self.get_column_place_holder(key, SQL_OP_SELECT, as_stmt))
                          )
        if len(clause) > 0 :
            return ' AND '.join(clause)
        else :
            return '1'

    def get_duplicate_key_clause(self, as_stmt):
        clause = []
        for field in self.data_fields:
            if self.fRdr.isDuplicateKeyUpdate(field):
                clause.append('%s=%s' % (field.attrib['column_name'].strip(),
                                         self.get_column_place_holder(field, SQL_OP_INSERT_DUPLICATE_UPDATE, as_stmt))
                              )
        if len(clause) > 0 :
            return ' ON DUPLICATE KEY UPDATE ' + ','.join(clause)
        else :
            return ''
    
    def get_table_comment(self):
        if not self.root.find(".//table_comment") is None:
            return "COMMENT='%s'" % self.root.find(".//table_comment").text.strip()
        else:
            return ''

    def is_only_select(self):
        if not self.root.find(".//is_only_select") is None:
            return self.root.find(".//is_only_select").text.strip() == 'true'
        else:
            return False

    def get_table_name(self):
        if not self.root.find(".//table_name") is None:
            return self.root.find(".//table_name").text.strip()
        else:
            return "__not_defined__"

    def get_alias(self):
        if not self.root.find(".//table_name") is None:
            if self.root.find(".//table_name").attrib.has_key('as'):
                return self.root.find(".//table_name").attrib['as'].strip()
        else:
            return  None
            
    def is_join_table(self):
        if "LEFT JOIN" in self.get_table_name():
            return True
        else:
            return False

    def get_column_place_holder(self, field, sql_op, as_stmt):
        data_type = self.fRdr.getType(field)
        if sql_op == SQL_OP_INSERT and self.fRdr.hasInsertVal(field):
            return self.fRdr.getInsertVal(field)
        elif sql_op == SQL_OP_UPDATE and self.fRdr.hasUpdateVal(field):
            return self.fRdr.getUpdateVal(field)
        elif as_stmt:
            return '?'
        elif DATATYPE_2_PLACEHOLDER.has_key(data_type):
            return DATATYPE_2_PLACEHOLDER[data_type];
        else:
            return '--';


    def gen_select_fields(self):
        field_names = [x.attrib['column_name'].strip() for x in self.fields]
        
        if self.root.find(".//joins") is None:
            return ','.join(field_names)
        elif self.get_alias() is None:
            print 'warning: alias table name should be defined when generate sql statement with join'
            return
                                            
        field_names = ['.'.join([self.get_alias(), x]) for x in field_names]    
        
        for join in self.joins:
            alias = join.attrib['as']
            for child in join.getchildren():
                if child.attrib.has_key('combine'):
                    name = ' AS ' . join([child.attrib['combine'], child.attrib['column_name']])
                else:
                    name = '.'.join([alias, child.attrib['column_name'].strip()])

                field_names.append(name)        
            # names = ['.'.join([alias, child.attrib['column_name'].strip()]) for child in join.getchildren()]
            # field_names.extend(names)
        
        return ','.join(field_names)

    def get_join_statement(self):
        if self.root.find(".//joins") is None:
            return ''

        s = []
        for join in self.joins:
            alias = join.attrib['as']
            s.append('LEFT JOIN %s AS %s ON %s '%(join.attrib['table_name'],alias, join.attrib['on']))            
        return ''.join(s)
            
    def gen_alias_statement(self):
        alias_statement = ''
        alias = self.get_alias()
        if alias:
            alias_statement = ' '.join([' AS', alias])
        
        return alias_statement

    def gen_select(self, as_stmt=False):
        s = 'SELECT %s FROM %s%s %sWHERE %s' % (
            self.gen_select_fields(),
            self.get_table_name(),
            self.gen_alias_statement(),
            self.get_join_statement(),
            self.get_select_where_clause(as_stmt))
        
        return s    
    
    def gen_delete(self, as_stmt=False):
        if self.is_join_table() or self.is_only_select():
            return ""
        
        return 'DELETE FROM %s WHERE %s' % (self.get_table_name(),
                                            self.get_where_clause(as_stmt))

    def gen_insert(self, as_stmt=False):
        if self.is_join_table()  or self.is_only_select():
            return ""
        
        field_names = []
        field_types = []
        field_values = []

        for field in self.fields:
            if field not in self.auto_fields:
                field_names.append(field.attrib['column_name'].strip())
                field_types.append(self.get_column_place_holder(field, SQL_OP_INSERT, as_stmt))

        return 'INSERT INTO %s(%s) VALUES(%s)%s' % (self.get_table_name(),
                                                  ','.join(field_names),
                                                  ','.join(field_types),
                                                  self.get_duplicate_key_clause(as_stmt))

    def gen_update(self, as_stmt=False):
        if self.is_join_table() or self.is_only_select():
            return ""
            
        field_setters = []

        for field in self.data_fields:
            if field not in self.auto_fields and not self.fRdr.isIgnoreOnUpdate(field):
                field_setters.append(
                    '%s=%s' % (field.attrib['column_name'].strip(),
                               self.get_column_place_holder(field, SQL_OP_UPDATE, as_stmt)))
        
        if 0 == len(field_setters):
            return ""
        
        return 'UPDATE %s SET %s WHERE %s' % (self.get_table_name(),
                                              ','.join(field_setters),
                                              self.get_where_clause(as_stmt))

    def gen_backup(self, as_stmt=False):
        if self.is_join_table() or self.is_only_select():
            return ""
        
        field_setters = []

        for field in self.data_fields:
            if field not in self.auto_fields and not self.fRdr.isIgnoreOnUpdate(field):
                field_setters.append(
                    '%s=%s' % (field.attrib['column_name'].strip(),
                               self.get_column_place_holder(field, SQL_OP_UPDATE, as_stmt)))

        return 'INSERT INTO %s_bak SELECT %s FROM %s WHERE %s' % (
            self.get_table_name(),
            "*", #self.gen_select_fields(),
            self.get_table_name(),
            self.get_where_clause(as_stmt))