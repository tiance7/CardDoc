# coding: utf-8
/************************************************************************
 * @file			persist${sqlParser.get_module_path()}${CLS_NAME}Dao.h
 * @brief
 * @author          Auto Generated.
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#ifndef __PERSIST_${sqlParser.get_module()}_${RAW_DATA_TYPE}_H__
#define __PERSIST_${sqlParser.get_module()}_${RAW_DATA_TYPE}_H__

#pragma once

#include <storage/DaoProxy.h>

#pragma pack(1)
typedef struct ${RAW_DATA_TYPE}
{
% for field in fields:
    %if fRdr.isString(field):
    ${fRdr.getType(field)}       ${fRdr.getName(field)}[${fRdr.getSize(field)}] ;          // ${fRdr.getComment(field)}
    %endif
    %if not fRdr.isString(field):
    ${fRdr.getType(field)}        ${fRdr.getName(field)};             // ${fRdr.getComment(field)}
    %endif
% endfor
    %for join in joins:
    %for child in join.getchildren():
    %if fRdr.isString(child):
    ${fRdr.getType(child)}       ${fRdr.getName(child)}[${fRdr.getSize(child)}] ;          // ${fRdr.getComment(child)}
    %endif
    %if not fRdr.isString(child):
    ${fRdr.getType(child)}        ${fRdr.getName(child)};             // ${fRdr.getComment(child)}
    %endif
    %endfor	
    %endfor
}${RAW_DATA_TYPE};
#pragma pack()

class ${CLS_NAME}Dao : public DaoProxy
{
    DAO_DECLARATION()
public:
    %if not sqlParser.is_char_obj():
    ${CLS_NAME}Dao(DaoStorage* pStorage, UINT32 uid=0);
    %else:
    ${CLS_NAME}Dao(DaoStorage* pStorage, UINT32 uid);
    %endif
    virtual ~${CLS_NAME}Dao(void);

    %for auto in sqlParser.get_auto_fields():
    virtual UINT64          GetKey()                    { return ${fRdr.getGetMethod(auto)}; };
    virtual void            SetKey(UINT64 key)          { ${fRdr.getSetMethod(auto, 'key')}; };
    %endfor

    %for getter in sqlParser.get_getters():
    ${getter}
    %endfor

    %for setter in sqlParser.get_setters():
    ${setter}
    %endfor

    virtual int             OnRow(ResultSetPtr& rs, UINT32 offset = 0);
    virtual int             Marshal(DaoOp* op);
    virtual int             Unmarshal(DaoOp* op);
%if len(sqlParser.get_auto_fields()) > 0:
    virtual int             OnInsert(DaoOp* op)     { return Unmarshal(op); }
%endif


    static char             FIELDS_STR_SELECT[];
    %if sqlParser.isDynTable():
    static char             CREATE_TABLE_SQL[];
    virtual const char*     GetCreateTableSql()     { return CREATE_TABLE_SQL; }
    %endif

protected:
    virtual int             BindSelect(iStatement* stmt);
    virtual int             BindInsert(iStatement* stmt);
    virtual int             BindUpdate(iStatement* stmt);
    virtual int             BindDelete(iStatement* stmt);
    virtual int             BindBackup(iStatement* stmt);
    virtual int             BindQuery(iStatement* stmt) ;

    int                     maxlen() {
        %if sqlParser.isDynTable():
        return ${fRdr.getLength(fields)}\
        %for join in joins:
+${fRdr.getLength(join.getchildren())}\
        %endfor 
 + DAO_TABLENAME_MAX + 2 + 2;
        %else:
        return ${fRdr.getLength(fields)}\
        %for join in joins: 
+ ${fRdr.getLength(join.getchildren())}\
        %endfor 
 + 2;
        %endif
    }

%if len(sqlParser.get_auto_fields()) > 0:
    virtual void            OnKey(UINT64 newKey) {
        %for auto in sqlParser.get_auto_fields():
        m_data.${fRdr.getName(auto)} = static_cast<${fRdr.getType(auto)}>(newKey);
        %endfor
    };
%endif

    ${RAW_DATA_TYPE}        m_data;

};

#endif /* __PERSIST_${sqlParser.get_module()}_${RAW_DATA_TYPE}_H__ */
