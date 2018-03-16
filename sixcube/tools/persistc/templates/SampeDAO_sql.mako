# coding: utf-8
DROP TABLE IF EXISTS `${sqlParser.get_table_name()}`;
CREATE TABLE  `${sqlParser.get_table_name()}` (
%for field in fields:
    %if fRdr.isMysqlString(field):
    `${fRdr.getColumn(field)}` ${fRdr.getMysqlType(field)}(${fRdr.getMysqlSize(field)}) ${fRdr.getMysqlNull(field)} ${fRdr.getMysqlAI(field)} ${fRdr.getMysqlDefault(field)},
    %endif
    %if not fRdr.isMysqlString(field):
    `${fRdr.getColumn(field)}` ${fRdr.getMysqlType(field)} ${fRdr.getMysqlNull(field)} ${fRdr.getMysqlAI(field)} ${fRdr.getMysqlDefault(field)},
    %endif
%endfor
    ${sqlParser.get_primary_columns()}
%for index in UINQUES:
    , UNIQUE KEY `${index.attrib['name']}` (${index.text})
%endfor
%for index in INDEXES:
    , KEY `${index.attrib['name']}` (${index.text})
%endfor
) ENGINE = InnoDB  DEFAULT CHARSET=utf8 ${sqlParser.get_table_comment()};
