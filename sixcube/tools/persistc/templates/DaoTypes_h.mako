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
	DAO_TYPE_OBJECT,			// 对象基类
	DAO_TYPE_PROXY,
	DAO_TYPE_TXN,               // 事务
%for typeId in typeIds:
    ${typeId},
%endfor
    DAO_TYPE_TEST_0,
    DAO_TYPE_TEST_1,
    DAO_TYPE_TEST_2,
    DAO_TYPE_TEST_3,
    DAO_TYPE_TEST_4,
    DAO_TYPE_TEST_5,
    DAO_TYPE_TEST_6,
    DAO_TYPE_TEST_7,
    DAO_TYPE_TEST_8,
    DAO_TYPE_TEST_9,
    DAO_TYPE_MAX
};
#endif /* __ENTITY_DAOTYPES_H__ */
