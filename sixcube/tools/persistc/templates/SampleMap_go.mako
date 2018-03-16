# coding: utf-8
package ${PACKAGE}

import (
	"database/sql"

	"sixcube/types"
	"sixcube/uninet/storage"
)

func init() {    
    storage.Register(${container.get_object_type()}, func(uid uint32) storage.PersistObject{
        return New${container.get_element_class()}(uid)
    })
}

type ${container.get_element_class()} struct {
	storage.PersistBase

    Objects map[${fRdr.getGoType(mapKey[0])}]*${element.get_classname()}Dao
% for field in refKeys:
    ${fRdr.getName(field)}        ${fRdr.getGoType(field)}             // ${fRdr.getComment(field)}
% endfor
}

func New${container.get_element_class()}(uid uint32) *${container.get_element_class()} {
	o := &${container.get_element_class()}{
		PersistBase: storage.PersistBase{
			ObjectUid:  uid,
			ObjectType: ${container.get_object_type()},
		},
		Objects: make(map[${fRdr.getGoType(mapKey[0])}]*${element.get_classname()}Dao),
	}
	return o
}

func (o *${container.get_element_class()}) maxlen() int {
    return ${fRdr.getLength(refKeys)} + 2
}

func (o *${container.get_element_class()}) SetUid(uid uint32) {
	o.PersistBase.ObjectUid = uid
	for _, obj := range o.Objects {
		if nil != obj {
			obj.SetUid(uid)
		}
	}
}

func (o *${container.get_element_class()}) Add${element.get_classname()}(elem *${element.get_classname()}Dao) int {
	if _, ok := o.Objects[elem.${fRdr.getName(mapKey[0])}]; ok {
		return -1
	} else {
		o.Objects[elem.${fRdr.getName(mapKey[0])}] = elem
		return 0
	}
}

func (o *${container.get_element_class()}) Del${element.get_classname()}(elem *${element.get_classname()}Dao) int {
	if _, ok := o.Objects[elem.${fRdr.getName(mapKey[0])}]; ok {
		delete(o.Objects, elem.${fRdr.getName(mapKey[0])})
		return 0
	} else {
		return -1
	}
}

func (o *${container.get_element_class()}) Find${element.get_classname()}(elemId ${fRdr.getGoType(mapKey[0])}) *${element.get_classname()}Dao {
	if elem, ok := o.Objects[elemId]; ok {
		return elem
	} else {
		return nil
	}
}

func (o *${container.get_element_class()}) Prepare(op int8) string {
	switch op {
	case storage.OP_SELECT:
	    return "SELECT ${element.gen_select_fields()} FROM ${element.get_table_name()} WHERE ${container.get_where_clause(True)}"
    default:
        return ""
	}
}

func (o *${container.get_element_class()}) Select(stmt *sql.Stmt) (rows *sql.Rows, err error) {
	return stmt.Query(
% for field in refKeys:
        o.${fRdr.getName(field)},
% endfor
    )
}

func (o *${container.get_element_class()}) OnRow(rows *sql.Rows) error {
	object := New${element.get_classname()}Dao(o.Uid())
	if err := object.OnRow(rows); err == nil {
		o.Objects[object.${fRdr.getName(mapKey[0])}] = object
		return nil
	} else {
		return err
	}
}

func (o *${container.get_element_class()}) Marshal(op *storage.PersistOp) int {
	var size int

	if op.Stream == nil {
		op.Stream = types.NewStreamBuffer(make([]byte, 0, o.maxlen()))
	}

    size += op.Stream.WriteUint8(o.ObjectFlag)
% for field in refKeys:
    size += op.Stream.Write${METHOD[fRdr.getGoType(field)]}(o.${fRdr.getName(field)})
% endfor

	for _, object := range o.Objects {
		if object != nil {
			size += object.Marshal(op)
		}
	}

    return size
}

func (o *${container.get_element_class()}) Unmarshal(op *storage.PersistOp) int {
	var size int

	if nil == op || nil == op.Stream {
		return -1
	}

    size += op.Stream.ReadUint8(&o.ObjectFlag)
% for field in refKeys:
    size += op.Stream.Read${METHOD[fRdr.getGoType(field)]}(&o.${fRdr.getName(field)})
% endfor

	for len(op.Stream.Bytes()) > 0 {
		object := New${element.get_classname()}Dao(o.Uid())
		size += object.Unmarshal(op)
		o.Objects[object.${fRdr.getName(mapKey[0])}] = object
	}

    return size
}

