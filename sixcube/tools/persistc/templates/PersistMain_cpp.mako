#coding:utf-8
/************************************************************************
* @file			persist/PersistMain.cpp
* @brief
* @author          Bob Lee (bob@sixcube.cn)
* @copyright		Sixcube Information Technology Co,. Ltd. (2012)
* @date
************************************************************************/

#include "stdafx.h"

#include <storage/DaoObject.h>

%for dao_header in DAOOBJS:
#include <${PREFIX}/${dao_header[1]}>
%endfor

void PersistMain()
{
    const DaoClass* pClass = NULL;

    pClass = DaoObject::theClass;

%for dao_type in DAOOBJS:
    pClass = ${dao_type[0]}::theClass;
%endfor

}