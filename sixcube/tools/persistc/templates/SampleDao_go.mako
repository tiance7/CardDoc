# coding: utf-8
package ${PACKAGE}

import (
	"database/sql"

	"sixcube/types"
	"sixcube/uninet/storage"
)

func init() {    
    storage.Register(${sqlParser.get_object_type()}, func(uid uint32) storage.PersistObject{
        return New${CLS_NAME}Dao(uid)
    })
}

type ${CLS_NAME}Dao struct {
	storage.PersistBase

% for field in fields:
    ${fRdr.getName(field)}			${fRdr.getGoType(field)}             // ${fRdr.getComment(field)}
% endfor
% for join in joins:
	% for child in join.getchildren():
    	${fRdr.getName(child)}    	${fRdr.getGoType(child)}             // ${fRdr.getComment(child)}
	% endfor	
% endfor

}

func New${CLS_NAME}Dao(uid uint32) *${CLS_NAME}Dao {
	o := &${CLS_NAME}Dao{
		PersistBase: storage.PersistBase{
			ObjectUid:  uid,
			ObjectType: ${sqlParser.get_object_type()},
		},
	}
	return o
}

func (o *${CLS_NAME}Dao) maxlen() int {
    return ${fRdr.getLength(fields)} + 2
}

func (o *${CLS_NAME}Dao) Prepare(op int8) string {
	switch op {
	case storage.OP_SELECT:
		return "${sqlParser.gen_select(True)}"

	case storage.OP_INSERT:
		return "${sqlParser.gen_insert(True)}"

	case storage.OP_UPDATE:
		return "${sqlParser.gen_update(True)}"

	case storage.OP_DELETE:
		return "${sqlParser.gen_delete(True)}"

	default:
		return ""
	}
}

func (o *${CLS_NAME}Dao) Select(stmt *sql.Stmt) (rows *sql.Rows, err error) {
	return stmt.Query(
    %for key in sqlParser.get_primary_fields():
        o.${fRdr.getName(key)},
    %endfor
    )
}

func (o *${CLS_NAME}Dao) OnRow(rows *sql.Rows) error {
	err := rows.Scan(
    %for field in fields:
        &o.${fRdr.getName(field)},
    %endfor
	% for join in joins:
	% for child in join.getchildren():
    	&o.${fRdr.getName(child)},
	% endfor	
% endfor
	)

	o.SetPersisted(err == nil)
	
	return err
}

func (o *${CLS_NAME}Dao) Insert(stmt *sql.Stmt) (res sql.Result, err error) {
	return stmt.Exec(
        %for field in fields:
        %if field not in sqlParser.get_auto_fields() and not fRdr.hasInsertVal(field):
        o.${fRdr.getName(field)},
        %endif
        %endfor
	)
}

func (o *${CLS_NAME}Dao) OnKey(newKey int64) {
    %for field in sqlParser.get_auto_fields():
	o.${fRdr.getName(field)} = ${fRdr.getGoType(field)}(newKey)
    %endfor
}

func (o *${CLS_NAME}Dao) Update(stmt *sql.Stmt) (res sql.Result, err error) {
	return stmt.Exec(
        %for field in sqlParser.get_data_fields():
        %if not fRdr.isIgnoreOnUpdate(field):
        o.${fRdr.getName(field)},
        %endif
        %endfor
        %for key in sqlParser.get_primary_fields():
        o.${fRdr.getName(key)},
        %endfor
	)
}

func (o *${CLS_NAME}Dao) Delete(stmt *sql.Stmt) (res sql.Result, err error) {
	return stmt.Exec(
        %for key in sqlParser.get_primary_fields():
        o.${fRdr.getName(key)},
        %endfor
	)
}

func (o *${CLS_NAME}Dao) Backup(stmt *sql.Stmt) (res sql.Result, err error) {
	return stmt.Exec(
        %for key in sqlParser.get_primary_fields():
        o.${fRdr.getName(key)},
        %endfor
	)
}

func (o *${CLS_NAME}Dao) Marshal(op *storage.PersistOp) int {
	var size int

	if op.Stream == nil {
		op.Stream = types.NewStreamBuffer(make([]byte, 0, o.maxlen()))
	}

    size += op.Stream.WriteUint8(o.ObjectFlag)
% for field in fields:
    size += op.Stream.Write${METHOD[fRdr.getGoType(field)]}(o.${fRdr.getName(field)})
% endfor

% for join in joins:
	% for child in join.getchildren():
		size += op.Stream.Write${METHOD[fRdr.getGoType(child)]}(o.${fRdr.getName(child)})
	% endfor	
% endfor	

    return size
}

func (o *${CLS_NAME}Dao) Unmarshal(op *storage.PersistOp) int {
	var size int

	if nil == op || nil == op.Stream {
		return -1
	}

    size += op.Stream.ReadUint8(&o.ObjectFlag)
% for field in fields:
    size += op.Stream.Read${METHOD[fRdr.getGoType(field)]}(&o.${fRdr.getName(field)})
% endfor

% for join in joins:
	% for child in join.getchildren():
		size += op.Stream.Read${METHOD[fRdr.getGoType(child)]}(&o.${fRdr.getName(child)})
	% endfor	
% endfor	

    return size
}
