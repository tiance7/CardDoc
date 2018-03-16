grammar protobuf;

options {
	language = Python;
	output = AST;
}

tokens {
	FIELDDEF;
	COMMENT;
	COMMENTS;
	FIELDS;
	ENUMS;
	TAILCOMMENT;
	FIELD_OPTION;
}

prog	: 	stmt+
		;

stmt 	: 	import_stmt 
    	|	message_stmt
    	|	enum_specifier
    	|	comment
    	;
    	
comment 
	:	LINE_COMMENT -> ^(COMMENT LINE_COMMENT)
	|   CSTYLE_COMMENT -> ^(COMMENT CSTYLE_COMMENT)
	;
	
 	
import_stmt
	:	'import' ID ';' ->^('import' ID)
	;

message_stmt
	:	'message'^ ID '{'!
			(field_stmt
			| comment
			| enum_specifier
			| option_stmt)+
		'}'!
	;
	
option_stmt
	:	'option'^ option_name '='! option_value ';'!
	;
	
option_name
	:	'db_store'
	|	'db_table'
	|	'db_obj_type'
	|	'primary' 
	| 	'index'
	;

option_value
	: ID
	| CSTRING
	| number
	;

field_stmt
	:	field_lable field_type ID '=' DEC field_option? ';' 
		-> ^(FIELDDEF field_lable field_type ID DEC field_option?)
	;
	
field_option
	: '[' option_name '=' ID ']'
		->^(FIELD_OPTION option_name ID)
	;

field_lable
	:	'required' 
	|	'repeated'
	;

field_type
	:	'int'
	|	'int32' 
	|	'uint32'
	| 	'char'
	|	'uchar'
	|	'short'
	|	'ushort'
	|	'int64'
	|	'uint64'
	|	'UINT16'
	|	'INT16'
	|	'INT32'
	|	'UINT32'
	|	'string'
	|	'BYTE'
	|	'ZGID'
	|	'float'
	|	ID
	;

enum_specifier
	:	'enum'^ '{'! ( enumerator | comment)*  '}'!
	|	'enum'^ ID '{'! (enumerator | comment)* '}'!
	;

enumerator
	:	ID '='^ constant_expression ';'!
	;
	
constant_expression
	:	primary_expression binary_operator^ constant_expression  
	|	'('! c=constant_expression ')'!
	|	unary_operator^ c=constant_expression
	| 	primary_expression
	;		

primary_expression
	:	number
	|	ID;
	
	
binary_operator
	:	'+'
	|	'<<'
	|	'|'
	;
unary_operator
	:	'-'
	|	'~'
	;


number
	:	HEX
	|	DEC
	|	OCT
	;

LINE_COMMENT
	:	'//'(~'\n')*'\n'
	;

CSTYLE_COMMENT
	:	'/*' ( options{greedy=false;} : .)* '*/'
	;

CSTRING
	:	'"'( EscapeSequence | ~('\\'|'"') )*'"'
	;		
fragment
EscapeSequence
	:	'\\' ('b'|'t'|'n'|'f'|'r'|'\"'|'\''|'\\')
	|	OctalEscape
	;
OctalEscape
	: '\\' ('0' ..'3')('0'..'7')('0'..'7')
	| '\\' ('0'..'7')('0'..'7')
	| '\\' ('0'..'7')
	;

ID	:	 ('a'..'z'|'A'..'Z'|'_')('a'..'z'|'A'..'Z'|'0'..'9'|'_')* ;

HEX	:	'0'('x'|'X') HexDigital+;
DEC	:	('0' | '1'..'9''0'..'9'*);
OCT	:	'0'('0'..'7')+;

fragment
HexDigital
	:	('0'..'9'|'a'..'f'|'A'..'F');

NEWLINE	: 	'\r'?'\n' { $channel=HIDDEN;} ;
WS	:	(' '|'\t')+ { $channel=HIDDEN; };

