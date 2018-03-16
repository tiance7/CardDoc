#coding:utf-8
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<${className} object_type='DOT_${rawType}' module="" skeleton="DaoProxy">
    <raw_type>${rawType}</raw_type>
    <statement>true</statement>
    <force_capture_select>false</force_capture_select>
    <force_capture_delete>false</force_capture_delete>
    <table_name>${tableName}</table_name>

    <fields>
%for col in columns:
        <field data_type="${f.getColType(columns[col])}"${f.getColSize(columns[col])}column_name="${columns[col].name}" nullable="${columns[col].null}" comment="">${f.getStructName(columns[col])}</field>
%endfor
    </fields>

    <indexes>
%for index in indexes:
        <index type='${f.getIndexType(indexes[index])}' name='${indexes[index].name}'>${f.getIndexFields(indexes[index])}</index>
%endfor
    </indexes>
</${className}>