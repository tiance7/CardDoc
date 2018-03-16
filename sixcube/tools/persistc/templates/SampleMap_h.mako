# coding: utf-8
/************************************************************************
 * @file            persist${container.get_module_path()}${container.get_element_class()}.h
 * @brief
 * @author          Auto Generated.
 * @copyright       Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#ifndef __PERSIST_${container.get_module()}_${container.get_object_type()}_H__
#define __PERSIST_${container.get_module()}_${container.get_object_type()}_H__
#pragma once

#include <storage/utils/${container.get_skeleton()}.h>
#include <${PREFIX}/${element.get_module_path()}${element.get_classname()}Dao.h>
%if fRdr.getMapIndexType(mapKey) == "std::string" and len(mapKey) == 2:
#include <utils/StlHelper.h>
%endif

%if len(refKeys) > 0:
#pragma pack(1)
typedef struct ${element.get_raw_type()}_MAP_REF
{
% for field in refKeys:
    %if fRdr.isString(field):
    ${fRdr.getType(field)}       ${fRdr.getName(field)}[${fRdr.getSize(field)}] ;          // ${fRdr.getComment(field)}
    %endif
    %if not fRdr.isString(field):
    ${fRdr.getType(field)}        ${fRdr.getName(field)};             // ${fRdr.getComment(field)}
    %endif
% endfor
} ${element.get_raw_type()}_MAP_REF;
#pragma pack()
%endif

class ${container.get_element_class()} : public ${container.get_skeleton()}<${fRdr.getMapIndexType(mapKey)}, ${element.get_classname()}Dao>
{
    DAO_DECLARATION()
public:
    %if not element.is_char_obj():
    ${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid= 0);
    %else:
    ${container.get_element_class()}(DaoStorage* pStorage, UINT32 uid);
    %endif
    virtual ~${container.get_element_class()}(void);

%for refKey in container.get_ref_keys():
    ${fRdr.getGetter(refKey)}
%endfor

    virtual int             addObject(${element.get_classname()}Dao* pObject) {
        return Bind(MakeIndex(pObject), pObject);
    };

    virtual int             BindSelect(iStatement* pStmt);
    %if len(container.get_ref_keys()) > 0:
    virtual int             BindDelete(iStatement* stmt);
    void                    SetRefKey(${container.get_ref_signature()});
    %endif
    %if container.has_ref_in_key():
    void                    SetRefInKey(std::vector<${fRdr.getType(container.get_ref_in_key())}>& valVec);
    %endif
    %if container.hasRowLimit():
    void                    SetRowIndex(UINT32 nIdx)    { m_nIndex = nIdx; }
    void                    SetRowLimit(UINT32 nLimit)  { m_nLimit = nLimit; }
    %endif

    virtual ${fRdr.getMapIndexType(mapKey)}     MakeIndex(${element.get_classname()}Dao* pObject){
        %if len(mapKey) == 1:
        return pObject->${fRdr.getGetMethod(mapKey[0])};
        %endif
        %if len(mapKey) == 2:
        return MakeIndex(pObject->${fRdr.getGetMethod(mapKey[0])}, pObject->${fRdr.getGetMethod(mapKey[1])});
        %endif
    };
    %if len(mapKey) == 2:
    
    static ${fRdr.getMapIndexType(mapKey)}      MakeIndex(${container.get_index_signature()}){
        %if fRdr.getMapIndexType(mapKey) == "std::string":
        return ConvertToString(${fRdr.getName(mapKey[0])}) + "-" + ConvertToString(${fRdr.getName(mapKey[1])});
        %else:
        return (UINT64(${fRdr.getName(mapKey[0])}) << 32) + ${fRdr.getName(mapKey[1])};
        %endif
    }
    %endif

protected:
    virtual int             selfMarshal(DaoOp* op);
    virtual int             selfUnmarshal(DaoOp* op);

protected:
    %if len(refKeys) > 0:
    ${element.get_raw_type()}_MAP_REF m_data;
    %endif
    %if container.has_ref_in_key():
    ${fRdr.getType(refInKey)} m_${fRdr.getName(refInKey)}[${fRdr.getSize(refInKey)}] ;    // ${fRdr.getComment(refInKey)}
    %endif
    %if container.hasRowLimit():
    UINT32 m_nIndex;
    UINT32 m_nLimit;
    %endif
}; 

#endif /* __PERSIST_${container.get_module()}_${container.get_object_type()}_H__ */
