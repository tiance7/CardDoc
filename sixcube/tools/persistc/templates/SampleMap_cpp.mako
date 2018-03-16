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

%if container.hasRowLimit():
static const char ${container.get_object_type()}_REF_STMT_SELECT[] = "SELECT ${element.gen_select_fields()} FROM ${element.get_table_name()}${element.gen_alias_statement()} ${element.get_join_statement()}WHERE ${container.get_where_clause(True)} LIMIT ?,?";
%else:
static const char ${container.get_object_type()}_REF_STMT_SELECT[] = "SELECT ${element.gen_select_fields()} FROM ${element.get_table_name()}${element.gen_alias_statement()} ${element.get_join_statement()}WHERE ${container.get_where_clause(True)}";
%endif

%if len(container.get_ref_keys()) > 0 and not element.is_only_select():
static const char ${container.get_object_type()}_REF_STMT_DELETE[] = "DELETE FROM ${element.get_table_name()} WHERE ${container.get_where_clause(True)}";
%endif

${container.get_element_class()}::${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid)
: ${container.get_skeleton()}<${fRdr.getMapIndexType(mapKey)}, ${element.get_classname()}Dao>(pStorage)
{
    SetUid(uid);
    SetType(${container.get_object_type()});
    m_stmtStr[DAO_CMD_SELECT] = ${container.get_object_type()}_REF_STMT_SELECT;
    %if len(container.get_ref_keys()) > 0:
    memset(&m_data, 0, sizeof(${element.get_raw_type()}_MAP_REF));
    %if not element.is_only_select():
    m_stmtStr[DAO_CMD_DELETE] = ${container.get_object_type()}_REF_STMT_DELETE;
    %endif
    %endif
    %if container.hasRowLimit():
    m_nIndex = 0;
    m_nLimit = 1;
    %endif
}

${container.get_element_class()}::~${container.get_element_class()}(void)
{
    ${container.get_skeleton()}<${fRdr.getMapIndexType(mapKey)}, ${element.get_classname()}Dao>::Clear();
}

int ${container.get_element_class()}::BindSelect(iStatement* pStmt)
{
    INT retNo = 0;
    INT idx = 0;
    %if len(container.get_ref_keys()) == 0:
    UNUSED_ARG(pStmt);
    UNUSED_ARG(idx);
    %endif
    
    %for key in container.get_ref_keys():
    retNo += pStmt->Bind${element.get_signature(key)}(idx++, m_data.${fRdr.getName(key)});
    %endfor
    %if container.has_ref_in_key():
    %for i in range(container.get_ref_in_key_size()):
    retNo += pStmt->Bind${element.get_signature(refInKey)}(idx++, m_${fRdr.getName(refInKey)}[${i}]);
    %endfor
    %endif
    %if container.hasRowLimit():
    retNo += pStmt->BindUInt32(idx++, m_nIndex);
    retNo += pStmt->BindUInt32(idx++, m_nLimit);
    %endif

    ASSERT(idx == pStmt->GetParamCount());
    return retNo;
}

%if len(container.get_ref_keys()) > 0 and not element.is_only_select():
int ${container.get_element_class()}::BindDelete(iStatement* pStmt)
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
%endif

%if container.has_ref_in_key():
void ${container.get_element_class()}::SetRefInKey(std::vector<${fRdr.getType(container.get_ref_in_key())}>& valVec)
{
    %for i in range(container.get_ref_in_key_size()):
    m_${fRdr.getName(refInKey)}[${i}] = (valVec.size() > ${i}) ? valVec[${i}] : 0;
    %endfor
}
%endif

int ${container.get_element_class()}::selfMarshal(DaoOp* op)	{
    int size = 0;
    %if len(refKeys) == 0:
    UNUSED_ARG(op);
    %endif

 % for key in refKeys:
    size += op->m_Stream->Write${element.get_go_signature(key)}(m_data.${fRdr.getName(key)});
% endfor
    %if container.has_ref_in_key():
    %for i in range(container.get_ref_in_key_size()):
    size += op->m_Stream->Write${element.get_go_signature(refInKey)}(m_${fRdr.getName(refInKey)}[${i}]);
    %endfor
    %endif
    %if container.hasRowLimit():
    size += op->m_Stream->WriteUint32(m_nIndex);
    size += op->m_Stream->WriteUint32(m_nLimit);
    %endif

    return size;
}

int ${container.get_element_class()}::selfUnmarshal(DaoOp* op)	{
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
    %if container.has_ref_in_key():
    %for i in range(container.get_ref_in_key_size()):
    size += op->m_Stream->Read${element.get_go_signature(refInKey)}(m_${fRdr.getName(refInKey)}[${i}]);
    %endfor
    %endif
    %if container.hasRowLimit():
    size += op->m_Stream->ReadUint32(m_nIndex);
    size += op->m_Stream->ReadUint32(m_nLimit);
    %endif
    
    return size;
}
