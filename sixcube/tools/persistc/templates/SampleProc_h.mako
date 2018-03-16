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

#include <das/DaoObject.h>

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
}${RAW_DATA_TYPE};

typedef struct ${RAW_DATA_TYPE}_RET
{
    PROC_RES        proc;
% for field in returns:
    %if fRdr.isString(field):
    ${fRdr.getType(field)}       ${fRdr.getName(field)}[${fRdr.getSize(field)}] ;          // ${fRdr.getComment(field)}
    %endif
    %if not fRdr.isString(field):
    ${fRdr.getType(field)}        ${fRdr.getName(field)};             // ${fRdr.getComment(field)}
    %endif
% endfor
}${RAW_DATA_TYPE}_RET;

#pragma pack()

class ${CLS_NAME}Proc : public DaoObject
{
	DAO_DECLARATION()
public:
	${CLS_NAME}Proc(DaoService* pService);
	virtual ~${CLS_NAME}Proc(void);

    INT32                   GetRes()    { return m_return.proc.nRes;    };
    UINT32                  GetRef()    { return m_return.proc.nRef;    };

	virtual BYTE*			GetDataInfo(UINT16& unit, UINT16& count, int capFlag);

    %for setter in sqlParser.get_setters():
    ${setter}
    %endfor

    % for field in returns:
    ${fRdr.getGetter(field, "m_return")}
    % endfor

    virtual int 			OnSelect(ResultSetPtr& rs, UINT32 offset = 0);


protected:
	virtual int				BindSelectParam(iStatement* stmt);


	${RAW_DATA_TYPE}		m_data;
    ${RAW_DATA_TYPE}_RET    m_return;

};

#endif /* __PERSIST_${sqlParser.get_module()}_${RAW_DATA_TYPE}_H__ */
