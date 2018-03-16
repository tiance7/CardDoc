/************************************************************************
 * @file			dao/DaoTypes.h
 * @brief
 * @author          Bob Lee (bob@sixcube.cn)
 * @copyright		Sixcube Information Technology Co,. Ltd. (2012)
 * @date
 ************************************************************************/
#ifndef __DAO_DAOTYPES_H__
#define __DAO_DAOTYPES_H__

enum DAO_TYPE {
	DAO_TYPE_OBJECT,			// 对象基类
	DAO_TYPE_PROXY,
	DAO_TYPE_TXN,               // 事务
    DOT__CACHE_LOGINS,
    DOT_ADMIN_SVR_LOG,
    DOT_CHAR_ACHIEVEMENT,
    DOT_CHAR_ACHIEVEMENT_ARRAY,
    DOT_CHAR_ACHIEVEMENT_MAP,
    DOT_ELO_SESSION,
    DOT_CHAR_ITEM,
    DOT_CHAR_ITEMS_ARRAY,
    DOT_CHAR_ITEMS_MAP,
    DOT_SP_TEST_5,
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
#endif /* __DAO_DAOTYPES_H__ */
