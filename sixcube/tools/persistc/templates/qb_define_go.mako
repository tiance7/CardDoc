#coding:utf-8
package ${package}

% if len(imps) > 0:
import (
    %for imp in imps:
        "${imp}"
    %endfor
)
% endif

type ${typeName} struct {
% for col in columns:
    ${f.get_col_name(columns[col])}       ${f.get_col_type(columns[col])}         ${f.get_col_tag(columns[col])}
% endfor
}

func (dt ${typeName})TableName() string {
    return "${tableName}"
}