#coding:utf-8
package ${PACKAGE}
import (
	"sixcube/uninet/storage"
)

func Init() {
    %for typeId in typeIds:
    storage.Register(${typeId[0]}, func() storage.PersistObject{ return New${typeId[2]}() } )
    %endfor
}
