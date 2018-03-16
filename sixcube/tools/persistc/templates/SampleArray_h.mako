/************************************************************************
 * @file			persist${container.get_module_path()}${container.get_element_class()}.h
 * @brief
 * @author          Auto Generated.
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#ifndef __PERSIST_${container.get_module()}_${container.get_object_type()}_H__
#define __PERSIST_${container.get_module()}_${container.get_object_type()}_H__

#pragma once
#include <storage/utils/DaoArray.h>
#include <${PREFIX}/${element.get_module_path()}${element.get_classname()}Dao.h>

% if len(refKeys) != 0:
#pragma pack(1)
typedef struct ${element.get_raw_type()}_REF
{
% for field in refKeys:
    %if fRdr.isString(field):
    ${fRdr.getType(field)}       ${fRdr.getName(field)}[${fRdr.getSize(field)}] ;          // ${fRdr.getComment(field)}
    %endif
    %if not fRdr.isString(field):
    ${fRdr.getType(field)}        ${fRdr.getName(field)};             // ${fRdr.getComment(field)}
    %endif
% endfor
} ${element.get_raw_type()}_REF;
#pragma pack()
% endif

class ${container.get_element_class()} : public ${container.get_skeleton()}<${element.get_classname()}Dao>
{
    DAO_DECLARATION()
public:
    %if not element.is_char_obj():
    ${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid=0);
    %else:
    ${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid);
    %endif
    virtual ~${container.get_element_class()}(void);

%for refKey in container.get_ref_keys():
    ${fRdr.getGetter(refKey)}
%endfor

	virtual int				BindSelect(iStatement* pStmt);


    void                    SetRefKey(${container.get_ref_signature()});

protected:
	virtual int				selfMarshal(DaoOp* op);
	virtual int				selfUnmarshal(DaoOp* op);
	virtual int				addObject(${element.get_classname()}Dao* pObj) {
		return AppendAt(pObj);
	};

private:
% if len(refKeys) != 0:
	${element.get_raw_type()}_REF	m_data;
% endif
};

#endif /* __PERSIST_${container.get_module()}_${container.get_object_type()}_H__ */
