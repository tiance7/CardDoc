tree grammar protobufWalker;

options {
	language = Python;
	output=template;
	tokenVocab=protobuf;
	ASTLabelType=CommonTree; // $label will have type CommonTree
	
}

scope symbol_table {
	types;
}

scope Field {
	label;
	type;
	id;
	method;	
}

@header {

}

prog
scope symbol_table;
@init {
	$symbol_table::types = dict()
}
	: 	(s += stmt)* 
		->prog(stmts={$s})
	;

stmt 	:	a=import_stmt
			-> {$a.st}
    	|	a=message_stmt
    		-> {$a.st}
    	|	a=enum_specifier
    		-> {$a.st}
    	|	a=comment
    		-> {$a.st}
		;

comment
	:		^(COMMENT LINE_COMMENT)
			-> comment(c={$LINE_COMMENT.text})
	|		^(COMMENT CSTYLE_COMMENT)
			-> comment(c={$CSTYLE_COMMENT.text})
	;

	
import_stmt
	:	^('import' ID)
		->import_stmt(module={$ID})
	;

message_stmt
scope {
  name;
  has_msg_type;
  db_store;
  db_obj_type;
  db_table;
  fields;   
}
@init {
  $message_stmt::has_msg_type=False
  $message_stmt::fields = []
}
@after {
	$symbol_table::types[$message_stmt::name] = $message_stmt[-1]
}
	:	^('message' ID{ $message_stmt::name = $ID.text; } p+=field_stmt*)
		->{$message_stmt::has_msg_type}? message_stmt(classname={$ID}, stat_list={$p}, field_list={$message_stmt::fields})
		->struct_stmt(classname={$ID.text}, stat_list={$p}, field_list={$message_stmt::fields}, db_table={$message_stmt::db_table}, db_obj_type={$message_stmt::db_obj_type})
	;

field_stmt
scope {
	is_custom_type;
	is_fix_str;
	fix_str_len;
	is_primary;
	ref_type;
	is_nest_type;
	label;
	type;
	id;
	order;
	method;
}
	:	^(FIELDDEF l=field_label t=field_type i=ID o=DEC field_option?) 
		{
			$field_stmt::label = $l.text
			$field_stmt::type = $t.text
			$field_stmt::id = $i.text
			$field_stmt::order = $o.text
			if $field_stmt::is_custom_type:
				$field_stmt::method = "custom"
			else:
				$field_stmt::method = "plain"
			
			if $symbol_table::types.has_key($t.text):
				$field_stmt::is_nest_type = True				
				$field_stmt::ref_type = $symbol_table::types[$t.text]
				#print "DEBUG>>>", $field_stmt::ref_type, dir($field_stmt::ref_type)
			$field_stmt::fix_str_len = '0'
			if $t.text.startswith("fixstr"):
				$field_stmt::is_fix_str = True
				$field_stmt::fix_str_len = $t.text[6:]									
			$message_stmt::fields.append($field_stmt[-1])
		}
		->{$field_stmt::is_nest_type}? custom_field_stmt(name={$i.text}, ref_type={$field_stmt::ref_type}, class_name={$message_stmt::name})
		->field_stmt(label={$l.text}, type={$t.text}, name={$i.text}, order={$DEC}, class_name={$message_stmt::name},
					 is_fix_str={$field_stmt::is_fix_str}, len={$field_stmt::fix_str_len},
					 is_primary={$field_stmt::is_primary})
	| ^('option' option_name v=option_value)
		{
	   		if ($option_name.text == "db_obj_type"): 
				$message_stmt::db_obj_type = $v.text;	
			elif ($option_name.text == "db_store"):
				$message_stmt::db_store = $v.text
			elif $option_name.text == "db_table":
				$message_stmt::db_table = $v.text			
		}
	|	e=embed_enum_specifier
		->{$e.st}
	|	c=comment
		->{$c.st}
	;
	
field_option 
	:	^(FIELD_OPTION o=option_name v=ID)
		{
			if $o.text == "primary" and v.text.lower() == "true":
				$field_stmt::is_primary = True
		}		
	;

option_name
	:	'db_store'
	|	'db_table'
	|	'db_obj_type'
	|	'primary'		
	|	'index'
	;

option_value
	:	ID
	|   CSTRING
	|	DEC
	;

field_label
	:	'required'
	|	'repeated'
	;
	
field_type
	:	custom_type { $field_stmt::is_custom_type = True}
	|	plain_type	{ $field_stmt::is_custom_type = False}
	;
		
custom_type
	:	ID
	|   'int64'
	|	'INT64'
	|	'uint64'
	|	'UINT64'
	|	'ZGID'
	;

plain_type
	:	'int'
	|	'int32' 
	|	'uint32'
	| 	'char'
	|	'uchar'
	|	'short'
	|	'ushort'
	|	'UINT16'
	|	'INT16'
	|	'INT32'
	|	'UINT32'
	|	'string'
	|	'BYTE'
	|	'float'
	;

enum_specifier
	:	^('enum' l=enumerator_list)
		->enum_specifier(list={$l.st})
	|	^('enum' ID l=enumerator_list)
		->enum_specifier(id={$ID}, list={$l.st})
	;
	
embed_enum_specifier
	:	^('enum' l=enumerator_list)
		->embed_enum_specifier(list={$l.st})
	|	^('enum' ID l=enumerator_list)
		->embed_enum_specifier(id={$ID}, list={$l.st})
	;

enumerator_list
	:	t+=enumerator*
		->{$t}
	;

enumerator
	:	^('=' ID v=constant_expression) 
		{
		   if ($ID.text == "THIS_MSG_TYPE"): $message_stmt::has_msg_type = True;
		}
		->enumerator(id={$ID.text}, value={$v.st})
	|	comment
		->{$comment.st}
	;
	
constant_expression
	:	^('+' p=primary_expression c=constant_expression)
		->add(a={$p.st}, b={$c.st})
	|	^('<<' primary_expression constant_expression)
	|	^('|' primary_expression constant_expression)
	|	^('-' c=constant_expression)
	|	^('~' c=constant_expression)
	|	p=primary_expression
		->{$p.st}
	;		

primary_expression
	:	number
		->{$number.text}
	|	ID
		->{$ID.text}	
	;

number
	:	HEX
	|	DEC
	|	OCT
	;
