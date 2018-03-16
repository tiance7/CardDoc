# coding: utf-8
/************************************************************************
 * @file			persist${sqlParser.get_module_path()}${CLS_NAME}Dao.cpp
 * @brief
 * @author          Auto Generated.
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#include "stdafx.h"
#include "${CLS_NAME}Dao.h"

#include <${PREFIX}/DaoIds.h>

DAO_REGISTRATION(${CLS_NAME}Dao, DaoObject, ${sqlParser.get_object_type()})

char ${CLS_NAME}Dao::FIELDS_STR_SELECT[] = "${sqlParser.gen_select_fields()}";
%if sqlParser.isDynTable():
char ${CLS_NAME}Dao::CREATE_TABLE_SQL[] = "CREATE TABLE IF NOT EXISTS `${sqlParser.get_table_name()}` (\
%for field in fields:
    %if fRdr.isMysqlString(field):
    `${fRdr.getColumn(field)}` ${fRdr.getMysqlType(field)}(${fRdr.getMysqlSize(field)}) ${fRdr.getMysqlNull(field)} ${fRdr.getMysqlAI(field)} ${fRdr.getMysqlDefault(field)},\
    %endif
    %if not fRdr.isMysqlString(field):
    `${fRdr.getColumn(field)}` ${fRdr.getMysqlType(field)} ${fRdr.getMysqlNull(field)} ${fRdr.getMysqlAI(field)} ${fRdr.getMysqlDefault(field)},\
    %endif
%endfor
    ${sqlParser.get_primary_columns()}\
%for index in UINQUES:
    , UNIQUE KEY `${index.attrib['name']}` (${index.text})\
%endfor
%for index in INDEXES:
    , KEY `${index.attrib['name']}` (${index.text})\
%endfor
) DEFAULT CHARSET=utf8 ${sqlParser.get_table_comment()};";
%endif

static char ${RAW_DATA_TYPE}_STMT_SELECT[] = "${sqlParser.gen_select(True)}";
%if not sqlParser.gen_insert(True) == "":
static char ${RAW_DATA_TYPE}_STMT_INSERT[] = "${sqlParser.gen_insert(True)}";
%endif
%if not sqlParser.gen_update(True) == "":
static char ${RAW_DATA_TYPE}_STMT_UPDATE[] = "${sqlParser.gen_update(True)}";
%endif
%if not sqlParser.gen_delete(True) == "":
static char ${RAW_DATA_TYPE}_STMT_DELETE[] = "${sqlParser.gen_delete(True)}";
%endif
%if sqlParser.has_backup_table():
static char ${RAW_DATA_TYPE}_STMT_BACKUP[] = "${sqlParser.gen_backup(True)}";
%endif

${CLS_NAME}Dao::${CLS_NAME}Dao(DaoStorage* pStorage, UINT32 uid)
: DaoProxy(pStorage)
{
    SetUid(uid);
    SetType(${sqlParser.get_object_type()});

    memset(&m_data, 0, sizeof(${RAW_DATA_TYPE}));
    %if sqlParser.isDynTable():
    SetFlag(PF_DYNTABLE);
    %endif

    m_stmtStr[DAO_CMD_SELECT] = ${RAW_DATA_TYPE}_STMT_SELECT;
    %if not sqlParser.gen_insert(True) == "":
    m_stmtStr[DAO_CMD_INSERT] = ${RAW_DATA_TYPE}_STMT_INSERT;
    %endif
    %if not sqlParser.gen_update(True) == "":
    m_stmtStr[DAO_CMD_UPDATE] = ${RAW_DATA_TYPE}_STMT_UPDATE;
    %endif
    %if not sqlParser.gen_delete(True) == "":
    m_stmtStr[DAO_CMD_DELETE] = ${RAW_DATA_TYPE}_STMT_DELETE;
    %endif
    %if sqlParser.has_backup_table():
    m_stmtStr[DAO_CMD_BACKUP] = ${RAW_DATA_TYPE}_STMT_BACKUP;
    %endif
}

${CLS_NAME}Dao::~${CLS_NAME}Dao(void)
{
}

int ${CLS_NAME}Dao::BindSelect(iStatement* pStmt)
{
	INT retNo = 0;
	INT idx = 0;

    %for key in sqlParser.get_primary_fields(True):
    retNo += pStmt->Bind${sqlParser.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor
    %for key in sqlParser.get_ref_where_fields():
    retNo += pStmt->Bind${sqlParser.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

	return retNo;
}

int ${CLS_NAME}Dao::BindInsert(iStatement* pStmt)
{   
    %if not sqlParser.gen_insert(True) == "":
    INT retNo = 0;
    INT idx = 0;

    %for field in fields:
    %if field not in sqlParser.get_auto_fields() and not fRdr.hasInsertVal(field):
    retNo += pStmt->Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)});
    %endif
    %endfor
    %for field in fields:
    %if fRdr.isDuplicateKeyUpdate(field):
    retNo += pStmt->Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)});
    %endif
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

    return retNo;
    %else:
    UNUSED_ARG(pStmt);
    return -1;
    %endif
}

int ${CLS_NAME}Dao::BindUpdate(iStatement* pStmt)
{
    %if not sqlParser.gen_update(True) == "":
    INT retNo = 0;
    INT idx = 0;

    %for field in sqlParser.get_data_fields():
    %if field not in sqlParser.get_auto_fields() and not fRdr.isIgnoreOnUpdate(field):
    retNo += pStmt->Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)});
    %endif
    %endfor
    %for key in sqlParser.get_primary_fields():
    retNo += pStmt->Bind${sqlParser.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

    return retNo;
    %else:
    UNUSED_ARG(pStmt);
    return -1;
    %endif
}

int ${CLS_NAME}Dao::BindDelete(iStatement* pStmt)
{
    %if not sqlParser.gen_delete(True) == "":
    INT retNo = 0;
    INT idx = 0;

    %for key in sqlParser.get_primary_fields():
    retNo += pStmt->Bind${sqlParser.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

    return retNo;
    %else:
    UNUSED_ARG(pStmt);
    return -1;
    %endif
}

int ${CLS_NAME}Dao::BindBackup(iStatement* pStmt)
{
    %if sqlParser.has_backup_table():
    INT retNo = 0;
    INT idx = 0;

    %for key in sqlParser.get_primary_fields():
    retNo += pStmt->Bind${sqlParser.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor
    ASSERT(idx == pStmt->GetParamCount());

    return retNo;
    %else:
    UNUSED_ARG(pStmt);
    return -1;
    %endif
}

int ${CLS_NAME}Dao::BindQuery(iStatement* pStmt)
{
    UNUSED_ARG(pStmt);
    return -1;
}

int ${CLS_NAME}Dao::OnRow(ResultSetPtr& rs, UINT32 offset /*=0*/)
{
	if (rs.Count() <= offset)
		return -1;

	iResultRow& row = rs[offset];

	INT idx = 0;

    %for field in fields:
    %if fRdr.isString(field):
    row.Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)}, ${fRdr.getSize(field)});
    %else:
    row.Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)});
    %endif
    %endfor
    %for join in joins:
    %for child in join.getchildren():
    %if fRdr.isString(child):
    row.Bind${sqlParser.get_signature(child)}(idx++, m_data.${fRdr.getName(child)}, ${fRdr.getSize(child)});
    %else:
    row.Bind${sqlParser.get_signature(child)}(idx++, m_data.${fRdr.getName(child)});
    %endif
    %endfor	
    %endfor

	row.Fetch();

	DaoObject::OnRow(rs, offset);

	return 1;
}

int	${CLS_NAME}Dao::Marshal(DaoOp* op)	{
	int size = 0;

	if (op->m_Stream == NULL) {
		op->m_Stream = new BytesStream(maxlen());
	}
    
    if (HasFlag(PF_DYNTABLE)) {
        size += op->m_Stream->WriteString(m_tblNow);
    }
    size += op->m_Stream->WriteUint8(m_Flag);
    %for field in fields:
    size += op->m_Stream->Write${sqlParser.get_go_signature(field)}(m_data.${fRdr.getName(field)});
    %endfor
    %for join in joins:
    %for child in join.getchildren():
    size += op->m_Stream->Write${sqlParser.get_go_signature(child)}(m_data.${fRdr.getName(child)});
    %endfor
    %endfor

	return size;
}

int	${CLS_NAME}Dao::Unmarshal(DaoOp* op)	{
	int size = 0;

	if (NULL == op || NULL == op->m_Stream){
		return -1;
	}
    
    if (HasFlag(PF_DYNTABLE)) {
        size += op->m_Stream->ReadString(m_tblNow, DAO_TABLENAME_MAX);
    }
    size += op->m_Stream->ReadUint8(m_Flag);
    %for field in fields:
    %if fRdr.isString(field):
    size += op->m_Stream->Read${sqlParser.get_go_signature(field)}(m_data.${fRdr.getName(field)}, ${fRdr.getSize(field)});
    %else:
    size += op->m_Stream->Read${sqlParser.get_go_signature(field)}(m_data.${fRdr.getName(field)});
    %endif
    %endfor
    %for join in joins:
    %for child in join.getchildren():
    %if fRdr.isString(child):
    size += op->m_Stream->Read${sqlParser.get_go_signature(child)}(m_data.${fRdr.getName(child)}, ${fRdr.getSize(child)});
    %else:
    size += op->m_Stream->Read${sqlParser.get_go_signature(child)}(m_data.${fRdr.getName(child)});
    %endif
    %endfor	
    %endfor

	return size;
}


