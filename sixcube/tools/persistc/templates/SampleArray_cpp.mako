# coding: utf-8
/************************************************************************
 * @file			persist${container.get_module_path()}${container.get_element_class()}.cpp
 * @brief
 * @author          Auto Generated.
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#include "stdafx.h"
#include "${container.get_element_class()}.h"

#include <${PREFIX}/DaoIds.h>

DAO_REGISTRATION(${container.get_element_class()}, DaoObject, ${container.get_object_type()})

static const char ${element.get_raw_type()}_REF_STMT_SELECT[] = "SELECT ${element.gen_select_fields()} FROM ${element.get_table_name()}${element.gen_alias_statement()} ${element.get_join_statement()}WHERE ${container.get_where_clause(True)}";

${container.get_element_class()}::${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid)
: DaoArray<${element.get_classname()}Dao>(pStorage)
{
    SetUid(uid);
    SetType(${container.get_object_type()});
% if len(refKeys) != 0:
    memset(&m_data, 0, sizeof(${element.get_raw_type()}_REF));
% endif
    m_stmtStr[DAO_CMD_SELECT] = ${element.get_raw_type()}_REF_STMT_SELECT;
}

${container.get_element_class()}::~${container.get_element_class()}(void)
{
    DaoArray<${element.get_classname()}Dao>::Clear();
}

int ${container.get_element_class()}::BindSelect(iStatement* pStmt)
{
	INT retNo = 0;
	INT idx = 0;

    %for key in container.get_ref_keys():
    retNo += pStmt->Bind${element.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

	return retNo;
}

void ${container.get_element_class()}::SetRefKey(${container.get_ref_signature()})
{
 % for field in refKeys:
    %if fRdr.isString(field):
    CopyString(m_data.${fRdr.getName(field)}, ${fRdr.getName(field)}, ${fRdr.getSize(field)}) ;
    %endif
    %if not fRdr.isString(field):
    m_data.${fRdr.getName(field)}  = ${fRdr.getName(field)};
    %endif
% endfor
}

int	${container.get_element_class()}::selfMarshal(DaoOp* op)	{
	int size = 0;
    %if len(refKeys) == 0:
    UNUSED_ARG(op);
    %endif
 % for key in refKeys:
    size += op->m_Stream->Write${element.get_go_signature(key)}(m_data.${fRdr.getName(key)});
% endfor

	return size;

}

int	${container.get_element_class()}::selfUnmarshal(DaoOp* op)	{
	int size = 0;
	%if len(refKeys) == 0:
    UNUSED_ARG(op);
    %endif
 % for key in refKeys:
    %if fRdr.isString(key):
    size += op->m_Stream->Read${element.get_go_signature(key)}(m_data.${fRdr.getName(key)}, ${fRdr.getSize(key)});
    %endif
    %if not fRdr.isString(key):
    size += op->m_Stream->Read${element.get_go_signature(key)}(m_data.${fRdr.getName(key)});
    %endif
% endfor
	return size;
}
