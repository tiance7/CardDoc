#coding:utf-8
package persists

import "sixcube/uninet/storage"

const (
%for typeId in OBJECT_IDS:
    ${typeId[0]} uint16 = ${typeId[1]}      // ${typeId[2]}
%endfor
)

func init() {
%for typeId in OBJECT_IDS:
	storage.ObjectTypeMap[${typeId[1]}] = "${typeId[0]}"
%endfor
}