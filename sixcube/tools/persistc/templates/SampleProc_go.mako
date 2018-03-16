# coding: utf-8
package test

import (
	"database/sql"
	"sixcube/core/network"
	"sixcube/persist"
	"sixcube/objects/_ids"
)

type ${CLS_NAME}Proc struct {
	persist.PersistBase

% for field in fields:
    ${fRdr.getName(field)}        ${fRdr.getGoType(field)}            // ${fRdr.getComment(field)}
% endfor
	Ret int
	Ref int
}

func New${CLS_NAME}Proc() *${CLS_NAME}Proc {
	o := &${CLS_NAME}Proc{}
    o.ObjectType = _ids.${sqlParser.get_object_type()}
	o.Object = o
	return o
}

func (o *${CLS_NAME}Proc) maxlen() int {
    return ${fRdr.getLength(fields)}+2
}

func (o *${CLS_NAME}Proc) Prepare(op int8) string {
	switch op {
	case persist.OP_SELECT:
		return "${sqlParser.gen_select(True)}"
    default:
        return ""
	}
}

func (o *${CLS_NAME}Proc) Select(stmt *sql.Stmt) (rows *sql.Rows, err error) {
	return stmt.Query(
    %for field in fields:
        o.${fRdr.getName(field)},
    %endfor
	)
}

func (o *${CLS_NAME}Proc) OnRow(rows *sql.Rows, storage storage.Storage) error {
	return rows.Scan(
		&o.Ret,
		&o.Ref,
	)
}


func (o *${CLS_NAME}Proc) Marshal(op *persist.PersistOp) int{
    var size int

    if op.Stream == nil {
        op.Stream = types.NewStreamBuffer(make([]byte, 0, o.maxlen()))
    }

    size += op.Stream.WriteUint8(o.ObjectFlag)
% for field in fields:
    size += op.Stream.Write${METHOD[fRdr.getGoType(field)]}(o.${fRdr.getName(field)})
% endfor

    return size
}

func (o *${CLS_NAME}Proc) UnMarshal(op *persist.PersistOp) int {
    var size int

    if nil == op || nil == op.Stream {
        return -1
    }

    size += op.Stream.ReadUint8(&o.ObjectFlag)
% for field in fields:
    size += op.Stream.Read${METHOD[fRdr.getGoType(field)]}(&o.${fRdr.getName(field)})
% endfor

    return size
}


