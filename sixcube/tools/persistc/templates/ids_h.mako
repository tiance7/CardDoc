#coding:utf-8
/************************************************************************
 * @file			dao/DaoTypes.h
 * @brief
 * @author          Bob Lee (bob@sixcube.cn)
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#ifndef __ENTITY_DAOTYPES_H__
#define __ENTITY_DAOTYPES_H__

enum DAO_TYPE {
%for typeId in OBJECT_IDS:
    ${typeId[0]} = ${typeId[1]},      // ${typeId[2]}
%endfor
};

#endif /* __ENTITY_DAOTYPES_H__ */

