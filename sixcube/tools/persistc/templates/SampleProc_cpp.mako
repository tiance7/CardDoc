# coding: utf-8
/************************************************************************
 * @file			persist${sqlParser.get_module_path()}${CLS_NAME}Dao.cpp
 * @brief
 * @author          Auto Generated.
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#include "stdafx.h"
#include "${CLS_NAME}Proc.h"

DAO_REGISTRATION(${CLS_NAME}Proc, DaoObject, ${sqlParser.get_object_type()})

static char ${RAW_DATA_TYPE}_STMT_SELECT[] = "${sqlParser.gen_select(True)}";

${CLS_NAME}Proc::${CLS_NAME}Proc(DaoService* pService)
: DaoObject(pService)
{
	SetType(${sqlParser.get_object_type()});
    SetFlag(DAO_IS_PROCEDURE);
%if sqlParser.foce_capture_select():
    SetFlag(DAO_CAPTURE_SELECT);
%endif
%if sqlParser.force_capture_delete():
    SetFlag(DAO_CAPTURE_DELETE);
%endif

	memset(&m_data, 0, sizeof(${RAW_DATA_TYPE}));
    memset(&m_return, 0, sizeof(${RAW_DATA_TYPE}_RET));


	m_stmtStr[DAO_CMD_SELECT] = ${RAW_DATA_TYPE}_STMT_SELECT;
}

${CLS_NAME}Proc::~${CLS_NAME}Proc(void)
{
}

BYTE* ${CLS_NAME}Proc::GetDataInfo(UINT16& unit, UINT16& count, int capFlag)
{
	data.dat_count	= 1;
    if (capFlag & CF_QUERY){
        data.dat_flag  |= DF_REFKEY;
	    data.dat_unit	= sizeof(${RAW_DATA_TYPE});
	    return (BYTE*)(&m_data);
    } else if (data.dat_flag & DF_REFKEY){
	    data.dat_unit	= sizeof(${RAW_DATA_TYPE});
	    return (BYTE*)(&m_data);
    } else {
        data.dat_unit	= sizeof(${RAW_DATA_TYPE}_RET);
	    return (BYTE*)(&m_return);
    }
}


int ${CLS_NAME}Proc::BindSelectParam(iStatement* pStmt)
{
	INT retNo = 0;
	INT idx = 0;

    %for field in fields:
    retNo += pStmt->Bind${sqlParser.get_signature(field)}(idx++, m_data.${fRdr.getName(field)});
    %endfor

    ASSERT(idx == pStmt->GetParamCount());

	return retNo;
}

int ${CLS_NAME}Proc::OnSelect(ResultSetPtr& rs, UINT32 offset /*=0*/)
{
	if (rs.Count() <= offset)
		return -1;

	iResultRow& row = rs[offset];

    if (false == row.HasField("res"))
        return -1;

	INT idx = 0;

    row.BindInt32(idx++, m_return.proc.nRes);
    row.BindUInt32(idx++, m_return.proc.nRef);
    %for field in returns:
    %if fRdr.isString(field):
    row.Bind${sqlParser.get_signature(field)}(idx++, m_return.${fRdr.getName(field)}, ${fRdr.getSize(field)});
    %else:
    row.Bind${sqlParser.get_signature(field)}(idx++, m_return.${fRdr.getName(field)});
    %endif
    %endfor

	row.Fetch();

	DaoObject::OnSelect(rs);

	return 1;
}

