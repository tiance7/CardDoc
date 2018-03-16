#!/usr/bin/python
# -*- coding: gbk -*-

from base_parser import *
import os

class CommentNode(ParseNode):
    def __init__(self, parent, comment, line_no):
        ParseNode.__init__(self, parent, "comment", comment)
        self.comment = comment
        self.line_no = line_no
    def Desc(self, offset):
        return "%s[%d]%s: %s\n" % (' ' * offset, self.line_no, "comment", self.comment)


class EnumFieldNode(ParseNode):
    def __init__(self, parent, enum_name, enum_value, line_no):
        ParseNode.__init__(self, parent, "enum_field_stmt", [enum_name, enum_value])
        self.enum_name = enum_name
        self.enum_value = enum_value        
        self.line_no = line_no
    def Desc(self, offset):
        return "%s[%d]%s: %s\n" % (' ' * offset, self.line_no, "enum_field_stmt", self.value)

class ClassMemberNode(ParseNode):
    def __init__(self, parent, member_type, member_name, array_num, line_no):
        ParseNode.__init__(self, parent, "member_data", [member_type, member_name, array_num])
        self.member_type = member_type
        self.member_name = member_name
        self.array_num = array_num
        self.line_no = line_no
    def Desc(self, offset):
        return "%s[%d]%s: %s\n" % (' ' * offset, self.line_no, "member_data", self.value)    

class CppParser(Parser):
    def __init__(self):
        Parser.__init__(self, 'cpp')

    def ParseStmt(self):
        token = self.lex.Scan()
        if self.lex.token == "comment":
            self.AddChildNode(CommentNode(self.current, self.lex.value, token.line_no))
        elif self.lex.token == "preprocesor":
            pass
        elif self.lex.token == "class":
            self.ParseClass()
        elif self.lex.token == "struct":            
            self.ParseClass("struct_stmt")
        elif self.lex.token == "enum":
            self.ParseEnum()
        elif self.lex.token == "typedef":
            self.ParseTypedef()        
        elif self.lex.token == "\0":
            #print "Parse END."
            pass        
        else:
            print "TODO UNKNOWN TOKEN: [%s][%s]\%s" % (self.lex.token, self.lex.value, self.lex.ShowError())

    def ParseTypedef(self):
        self.lex.Scan()
        while self.lex.token != ";":
            self.lex.Scan()
            
    def ParseClass(self, stmt="class_stmt"):
        class_name = self.Expect("identifier")
        class_node = ParseNode(self.current, stmt, class_name)
        self.AddChildNode(class_node)

        token, value, line_no = self.lex.Scan().ToTriList()
        if self.lex.token == ';':
            # forward declaration
            return
        elif self.lex.token == ":":
            # inherit
            token, value, line_no = self.lex.Scan().ToTriList()
            if token == 'public':
                self.Expect("identifier")
            elif token == 'identifier':
                pass
        elif self.lex.token == 'comment':
            step = 1
            self.AddChildNode(CommentNode(class_node, self.lex.value, line_no))
            token, value, line_no = self.lex.Scan().ToTriList()
            while token == 'comment':
                self.AddChildNode(CommentNode(class_node, value, line_no))
                step += 1                
                token, value, line_no = self.lex.Scan().ToTriList()
            self.lex.Undo(step)
        else:
            self.lex.Undo(1)
        self.Consume("{")
        token, value, line_no = self.lex.Scan().ToTriList()
        while self.lex.token != '}':
            if self.lex.token in ['public', 'private', 'protected']:
                self.Consume(':')
            elif self.lex.token in 'comment':
                self.AddChildNode(CommentNode(class_node, self.lex.value, line_no))
            elif self.lex.token == ";":                
                pass
            elif self.lex.token == "enum":
                self.current = class_node
                self.ParseEnum()
            elif self.lex.token == "typedef":
                self.ParseTypedef()
            else:
                self.current = class_node
                self.lex.Undo(1)
                self.ParseClassMember()
            token, value, line_no = self.lex.Scan().ToTriList()
        self.Consume(";")
        self.current = class_node.parent

    
    def ParseClassMember(self):
        """
        C++ class member is variety; 
        data member
            usual member
            member is array
        member function:
            construct
                identifier ( para_list );
                identifier ( para_list ) { }
            destructor
                ~identifier ( para_list );
                ~identifier ( para_list ) {}
            usual function
                [type | identifier] identifer( para_list );
                [type | identifier] identifer( para_list ) { stmts; }        
        """
        #print "in class token/value [%s]/[%s]" % (self.lex.token, self.lex.value)
        first_field_token, first_field_value = self.lex.Scan().ToList()
        token, value = self.lex.Scan().ToList()
        step = 2
        while True:            
            if token == '(':
                while token != ')':
                    token, value = self.lex.Scan().ToList()
                token, value = self.lex.Scan().ToList()
                if token == ';':
                    self.ParseMemberFunction()
                    return
                elif token in ['{', ':'] :
                    while token != '}':
                        token, value = self.lex.Scan().ToList()
                    self.ParseInlineFunction()
                    return
                elif token == '=':
                    self.Expect('number')
                    self.Consume(';')
                    return
                else:
                    raise SyntaxError
            elif token == ';':
                break
            else:
                token, value = self.lex.Scan().ToList()
                step += 1
        self.lex.Undo(step)          
        self.ParseMemberData()                    

    def ParseMemberData(self):
        var_type = self.ParseType()
        var_name = self.Expect('identifier');
        while True:            
            token, value, line_no = self.lex.Scan().ToTriList()        
            # type identifier;
            if token == ';':
                self.AddChildNode(ClassMemberNode(self.current, var_type, var_name, None, line_no))                
                break
            elif token == '[':
                array_number = self.ParseExperssion()            
                self.AddChildNode(ClassMemberNode(self.current, var_type, var_name, array_number, line_no))
                self.Consume(']')
                self.Consume(';')
                break
            elif token == ',':
                self.lex.Scan()
                self.AddChildNode(ClassMemberNode(self.current, var_type, var_name, None, line_no))
                var_name = self.lex.value
            elif token == ":":
                self.Consume('number');                                                  
                self.Consume(';');
                self.AddChildNode(ClassMemberNode(self.current, var_type, var_name, None, line_no))
                break
            else:
                raise SyntaxError
            
    def ConvertTypeName(self, typename):
        if typename == "unsignedlong": return "ULONG"
        if typename == "unsignedint": return "UINT32"
        if typename == "unsignedshort": return "UINT16"
        if typename == "unsignedchar": return "BYTE"
        return typename
        
    def ParseType(self):
        first_token, first_value = self.lex.Scan().ToList()
        var_type = first_value
            
        expect_id_number = 0
        token, value = self.lex.Scan().ToList()
        while True:            
            if expect_id_number == 0 and token == 'identifier':
                self.lex.Undo(1)
                return self.ConvertTypeName(var_type)
            elif expect_id_number > 0 and token in ['identifier', 'type']:
                var_type += value
                expect_id_number -= 1
            elif token == '::':
                expect_id_number += 1
                var_type += token            
            elif token == '<':
                expect_id_number += 1
                var_type += '<'
            elif token == '>':
                var_type += '>'
            elif token == "type":
                var_type += value
            else:
                raise SyntaxError
            token, value = self.lex.Scan().ToList()
        raise SyntaxError             
            
    def ParseMemberFunction(self):
        pass
        """
        self.AddChildNode(ParseNode(self.current, "member_method", first_field_token))
        self.lex.Scan()
        while self.lex.token != ')':
            self.lex.Scan()
        self.lex.Scan()
        if self.lex.token == ";":
            return
        elif self.lex.token == "{":
            while self.lex.token != "}":
                self.lex.Scan()
        """        
    def ParseInlineFunction(self):
        pass
    
    def ParseEnum(self):
        self.lex.Scan()
        enum_name = ""
        if self.lex.token == "identifier":
            enum_name = self.lex.value
            self.TryConsume("comment")
            self.Consume("{")
        elif self.lex.token != '{':
            raise SyntaxError
        #print "enum %s begin" % enum_name
        enum_node = ParseNode(self.current, 'enum_stmt', enum_name)
        self.AddChildNode(enum_node)

        token = self.lex.Scan()
        while self.lex.token != '}':
            if self.lex.token == "comment":
                self.AddChildNode(CommentNode(enum_node, self.lex.value, token.line_no))
            else:
                self.current = enum_node
                self.lex.Undo(1)
                self.ParseEnumField()
            token = self.lex.Scan()
        self.current = enum_node.parent
        self.Consume(";")
        #print "enum %s end" % enum_name

    def ParseEnumField(self):
        #print "in enum token/value: [%s]/[%s]:" % (self.lex.token, self.lex.value)
        token, value, line_no = self.lex.Scan().ToTriList()
        if token == ';':
            return
        if token != 'identifier':
            raise SyntaxError
       
        node = EnumFieldNode(self.current, value, None, line_no)
        self.AddChildNode(node)
            
        token, value, line_no = self.lex.Scan().ToTriList()
        while token == "comment":
            self.AddChildNode(CommentNode(self.current, value, line_no))
            token, value, line_no = self.lex.Scan().ToTriList()
            
        if token == '=':            
            node.enum_value = self.ParseExperssion()
            node.value[1] = node.enum_value  
            return
        elif token in [',', '}']:            
            if token == '}':
                self.lex.Undo()
            return

        print self.lex.token
        raise SyntaxError

    def ParseExperssion(self):
        expr = '' 
        token = self.lex.Scan()
        while token.token not in [',', '}', ']']:
            if token.token in ["identifier", "number"]:
                expr += token.value
            elif self.lex.token == "comment":
                self.AddChildNode(CommentNode(self.current, token.value, token.line_no))
            else:
                expr += token.token
            token = self.lex.Scan()
        if token.token != ',':
            self.lex.Undo(1)
        return expr
    
        #print self.lex.token, self.lex.value    
    def ParseStruct(self):
        struct_name = self.Expect("identifier")
        struct_node = ParseNode(self.current, 'struct_stmt', struct_name)
        self.AddChildNode(struct_node)
        self.Consume("{")
        self.lex.Scan()
        while self.lex.token != '}':
            self.current = struct_node
            self.ParseStructField()
            self.lex.Scan()
        self.current = struct_node.parent
        self.Consume(";")

    def ParseStructField(self):
        #print "in class token/value [%s]/[%s]" % (self.lex.token, self.lex.value)
        first_field_token = self.lex.value
        self.lex.Scan()
        if self.lex.token == '(': # 没有返回值的函数
            self.ParseFunction(first_field_token)            
        elif self.lex.token == "identifier": 
            second_field_token = self.lex.value
            self.lex.Scan()
            if self.lex.token == ";": # 成员变量
                self.AddChildNode(ParseNode(self.current, "member_variable", [first_field_token, second_field_token]))
            elif self.lex.token=="(":
                self.ParseFunction(first_field_token)
            else:
                #raise SyntaxError
                pass


if __name__ == "__main__":
    pass
    
    