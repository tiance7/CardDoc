#!/usr/bin/python
# -*- coding: gbk -*-

import sys
import time
import os
import os.path
import glob
from const import FIXSTR_TAG
from printer import Printer
from proto_handler import FindCachedProtoTypes
from proto_parser import ProtoParser

"""
# erlang 自动生成工具
# 01. 所有的结构体和类会转化成元组,数组用LIST表示
# 02. 一个类型定义的hrl
# 03. 一个编码解码模块
# 04. 嵌套类处理
# 05. 枚举的处理：枚举用宏定义实现,枚举名如果在嵌套类中，宏名会加上类名
# 
# 
# Generate process
# 01. Find the dependency around Type
# 02. sort the class according the type
# 03. Generate
"""

gerl_type_dict = {"int": "INT32",
                  "char": "INT8",
                  "short": "INT16",
                  "UINT32": "UINT32",
                  "INT32": "INT32",
                  "UINT16": "UINT16",
                  "INT16": "INT16",
                  "BYTE": "UINT8",
                  "ZGID": "UINT64",
                  "bool": "INT32",
                  "float": "FLOAT",
                  "double": "DOUBLE",
                  "UINT64": "UINT64",
                  "INT64": "INT64",
                  "CHAR": "INT8",
                  "INT": "INT32",
                  "UINT8": "UINT8",
                  "FLOAT": "FLOAT"};


class ErlangGenerator:
    def __init__(self, erl_printer, hrl_printer):
        self.enum_list = set()
        self.class_dict = dict() # a class to module dict
        self.package_list = []
        self.has_namespace = False
        self.namespace_name = ''
        self.offset = 0
        self.erl_printer = erl_printer
        self.hrl_printer = hrl_printer
        self.buildin_type = [
            "int", "char", "short", "UINT32", "INT32", "string", "std::string",
            "UINT16", "INT16", "BYTE", "ZGID", "bool", "float", "double",
            "UINT64", "INT64", "CHAR", "INT", "UINT8", "FLOAT"
        ]

    def OnAddNode(self, node):
        if node.token == "package":
            self.package_list.append(node)
        elif node.token == "enum_stmt":
            self.enum_list.add(node)
        elif node.token == "message_stmt":
            self.class_dict[node.value] = "?MODULE"

    def IsEnumType(self, type_name):
        for enum in self.enum_list:
            #print "enum:", enum
            if enum.value == type_name:
                return True
        return False

    def IsMessageType(self, type_name):
        return self.class_dict.has_key(type_name)

    def IsValidType(self, type_name):
        if type_name in self.buildin_type:
            return True
        if self.IsEnumType(type_name):
            return True
        if self.IsMessageType(type_name):
            return True
        return False


    def DetermineOuputPath(self, input_file_path):
        basename = os.path.basename(os.path.splitext(input_file_path)[0])
        hrl_name = "pb%s.hrl" % basename
        erl_name = "pb%s.erl" % basename
        if self.outdir != None:
            hrl_path = os.path.join(self.outdir, hrl_name)
            erl_path = os.path.join(self.outdir, erl_name)
        else:
            hrl_path = None
            erl_path = None
        return hrl_name, hrl_path, erl_name, erl_path

    def Generate(self, tree, input_file_path):
        self.input_dir = os.path.dirname(input_file_path)

        #header_name, header_path, module_name, module_path = self.DetermineOuputPath(input_file_path)
        #self.GenerateHeader(module_name)
        s = tree.Apply(self)

    def BeginNode(self, node):
        result = ''
        if node.token == "import_stmt":
            self.ImportFile(node.value)
            #self.printer.AppendLine('-include("%s.pb.hrl").' % node.value)
        elif node.token == "package_stmt":
            self.namespace_name = node.value
            self.has_namespace = True
        elif node.token == "enum_stmt":
            if node.value == "unnamed":
                #self.hrl_printer.AppendLine("enum {")
                pass
            else:
                #self.hrl_printer.AppendLine("enum %s {" % (node.value))
                pass
                #self.hrl_printer.IncIndent()
        elif node.token == "enum_field_stmt":
            if node.value[0] != "THIS_MSG_TYPE":
                self.hrl_printer.AppendLine("-define(%s, %s)." % (node.value[0], node.value[1]))
            else:
                pass
        elif node.token == "comment":
            #self.hrl_printer.AppendLine("%%%%%% %s" % node.value)
            pass
        elif node.token in ["root", "option_stmt"]:
            pass
        elif node.token == "message_stmt":
            #self.GenerateMessageDef(node)
            pass
        elif node.token == "struct_stmt":
            self.printer.AppendLine("struct %s {" % (node.value))
            self.printer.IncIndent()
        elif node.token == "struct_field_stmt":
            if len(node.value) == 2:
                self.printer.AppendLine("%s %s;\n" % (node.value[0], node.value[1]))
            else:
                self.printer.AppendLine("%s %s[%s];\n" % (node.value[0], node.value[1], node.value[2]))
        elif node.token == "field_stmt":
            #print node.value
            field_lable = node.value[0]
            field_type = node.value[1]
            field_name = node.value[2]
            if not self.IsValidType(field_type):
                print "TYPE: %s is not declared" % field_type

            first = False
            if not hasattr(node.parent, "first"):
                first = True
                node.parent.first = True

            if field_lable != "repeated":
                if FIXSTR_TAG not in field_type:
                    if first:
                        #self.hrl_printer.AppendLine(("%s \t\t%% %s " % (field_name, self.GetCppType(field_type))))
                        pass
                    else:
                        #self.hrl_printer.AppendLine((",%s \t\t%% %s " % (field_name, self.GetCppType(field_type))))
                        pass
                else:
                #self.hrl_printer.AppendLine("char %s[%d];" % (field_name, self.GetFixStrLen(field_type)))
                    pass
            else:
                assert FIXSTR_TAG not in field_type
                #self.hrl_printer.AppendLine("%s=[], \t\t%% repeated %s" % (field_name, self.GetCppType(field_type)))
        else:
            print node.token
        return  result

    def EndNode(self, node):
        if node.token == "enum_stmt":
            #self.hrl_printer.DecIndent()
            #self.hrl_printer.AppendLine("};\n")
            pass
        elif node.token in ["message_stmt", "struct_stmt"]:
            self.GenerateMessageMethod(node)
            #self.hrl_printer.AppendLine("});\n")
            #self.hrl_printer.DecIndent()
            pass
        return ''

    def GetParamType(self, var_type):
        """
        Convert parameter type to C++ type.
        now there are two rules:
        1. All build-in type pass by value, otherwise pass by reference.
        2. We use std::string to represent string type.
        """
        if var_type in ['int', 'int32', 'uint', 'uint32', 'byte', 'int64', 'UINT32', 'UINT16', 'INT32', 'float']:
            return var_type
        elif self.IsEnumType(var_type):
            return var_type
        elif FIXSTR_TAG in var_type:
            return "const std::string&"
        elif var_type == 'string':
            return "const std::%s&" % var_type
        else:
            return "const %s&" % var_type

    def GetParamName(self, var_name):
        if len(var_name) > 2 and var_name[:2] == 'm_':
            return var_name[2:]
        else:
            return '_' + var_name

    def GeneratePara(self, node):
        assert node.token == 'field_stmt'

        var_lable, var_type, var_name = node.value[0:3]

        if var_lable in ['required', 'optional']:
            return "%s %s" % (self.GetParamType(var_type), self.GetParamName(var_name))
        elif var_lable == 'repeated':
            return "const std::vector<%s>& %s" % (self.GetCppType(var_type), self.GetParamName(var_name))
        else:
            raise "%s" % var_lable

    def GenerateReadFromStream(self, node):
        self.printer = self.erl_printer
        self.erl_printer.AppendLine("")
        self.printer.AppendLine("%%%%%% decode %s " % node.value)
        self.printer.AppendLine("serialize(decode, %s, BinData0) ->" % self.GetThisMsgType(node))
        self.printer.IncIndent()
        memberCount = 0
        decodeindex = 0
        cache_list = []
        val_name_list = []

        def flush_cache(cache_list, decodeindex):
            if len(cache_list) == 0:
                return decodeindex, []
            line = ""
            for t in cache_list:
                line += "%s:?%s, " % (t[0], t[1])
                val_name_list.append(t[0])
            self.printer.AppendLine("<<%sBinData%d/binary>> = BinData%d," %
                                    (line, decodeindex + 1, decodeindex))
            return decodeindex + 1, []

        for child in node.childs:
            if child.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = child.value
            erl_val_name = ValName(field_name)
            if field_lable == "required":
                if self.IsEnumType(field_type):
                    cache_list.append((erl_val_name, "INT32"))
                elif FIXSTR_TAG in field_type or field_type in ["FLOAT", "float", "string"] or\
                     self.IsMessageType(field_type):
                    decodeindex, cache_list = flush_cache(cache_list, decodeindex)
                    A = "{%s, BinData%d} = decode(%s, BinData%d)," %\
                        (erl_val_name, decodeindex + 1, ErlAtom(field_type), decodeindex)
                    decodeindex += 1
                    self.printer.AppendLine(A)
                    val_name_list.append(erl_val_name)
                else:
                    cache_list.append((ValName(field_name), gerl_type_dict[field_type]))

            elif field_lable == "repeated":
                decodeindex, cache_list = flush_cache(cache_list, decodeindex)

                def GenDecodeFun(field_type):
                    if self.IsEnumType(field_type):
                        return "fun(__VAR__) -> <<Val:?INT32, Remain/binary>>=__VAR__, {Val, Remain} end"
                    elif field_type in ["string", "FLOAT", "float"] or\
                         self.IsMessageType(field_type):
                        return "fun(__VAR__)-> decode(%s, __VAR__) end" % (ErlAtom(field_type))
                    else:
                        return "fun(__VAR__) -> <<Val:?%s, Remain/binary>>=__VAR__, {Val, Remain} end" % gerl_type_dict[
                                                                                                         field_type]

                decode_fun = GenDecodeFun(field_type)
                self.printer.AppendLine("{%s, BinData%d} = decode_list(%s, BinData%d)," %
                                        (ValName(field_name), decodeindex + 1, decode_fun, decodeindex))
                decodeindex += 1
                val_name_list.append(ValName(field_name))
        decodeindex, cache_list = flush_cache(cache_list, decodeindex)
        self.printer.AppendLine("{%s, BinData%s};" %
                                (FormatValNameList(val_name_list), decodeindex))
        self.printer.DecIndent()

    def GenerateWriteToStream(self, node):
        self.printer = self.erl_printer
        self.erl_printer.AppendLine("%%%%%% encode %s" % node.value)
        match = ""
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            field_lable, field_type, field_name, field_index = field.value
            if match != "":
                match += ", "
            match += "%s" % (ValName(field_name))

        self.erl_printer.AppendLine("serialize(encode, %s, {%s}) ->" % (self.GetThisMsgType(node), match))
        self.printer.IncIndent()

        cache_list = []
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = field.value
            erl_var_name = ValName(field_name)
            if field_lable == "required":
                if self.IsEnumType(field_type):
                    cache_list.append((erl_var_name + ":", "?INT32"))
                elif FIXSTR_TAG in field_type:
                    leng = field_type[len(FIXSTR_TAG):]
                    cache_list.append(("(encode_string(%s, %s))" % (erl_var_name,
                                                                    leng),
                                       "/binary"))
                elif field_type == "string":
                    cache_list.append(("(encode_string(%s, length(%s)))" %
                                       (erl_var_name, erl_var_name), "/binary"))
                elif self.IsMessageType(field_type):
                    cache_list.append(("(serialize(encode, %s, %s))" %
                                       (ErlAtom(field_type), erl_var_name),
                                       "/binary"))
                else:
                    cache_list.append((erl_var_name, ":?%s" % gerl_type_dict[field_type]))

            elif field_lable == "repeated":
                def GenDecodeFun(field_type):
                    if self.IsEnumType(field_type):
                        return "fun(__VAR__) -> <<__VAR__:?INT32>> end"
                    elif field_type == "string":
                        return "fun(__VAR__) -> encode_string(__VAR__, length(__VAR__)) end"
                    elif self.IsMessageType(field_type):
                        return "fun(__VAR__) -> encode(%s, __VAR__) end" % (ErlAtom(field_type))
                    else:
                        return "fun(__VAR__) -> <<__VAR__:?%s>> end" % gerl_type_dict[field_type]

                encode_fun = GenDecodeFun(field_type)
                cache_list.append(("(encode_list(%s, %s))" % (encode_fun, erl_var_name),
                                   "/binary"))

        self.printer.AppendLine("<<")
        index = 0
        for t in cache_list:
            name, type = t
            if index > 0:
                self.printer.AppendSameLine(", ")
                if index % 1 == 0:
                    self.printer.AppendLine("")
            self.printer.AppendSameLine("%s%s" % (name, type))
            index += 1
        self.printer.AppendSameLine(">>;")
        self.printer.DecIndent()

    def NeedConstructor(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    return True
        return False

    def GetThisMsgType(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    return "?" + child.childs[0].value[1]
        return ErlAtom(node.value)

    def GenerateMessageDef(self, node):
        if self.NeedConstructor(node):
            self.hrl_printer.AppendLine("-record(msg%s, " % (node.value))
            pass
        else:
            self.hrl_printer.AppendLine("-record(msg%s, " % (node.value))
            pass
        self.hrl_printer.AppendSameLine("{")
        self.hrl_printer.IncIndent()
        # Constructor from Message

    def GenerateMessageMethod(self, node):
        if self.NeedConstructor(node):
            pass
            #self.GenerateReadConstructor(node)
            #self.GenerateWriteConstructor(node)
        else:
            #self.GenerateSimpleConstructor(node)
            pass
        self.GenerateReadFromStream(node)
        self.GenerateWriteToStream(node)

    def GetCppType(self, typename):
        if typename == "string":
            return "std::string"
        else:
            return typename

    def ImportFile(self, filename):
        """
        Extract all enum and message define from the import file
        """
        import_file_path = os.path.join(self.input_dir, filename + ".proto")
        enum_list, class_list = FindCachedProtoTypes(import_file_path)
        self.enum_list = self.enum_list.union(enum_list)
        for c in class_list:
            assert not self.class_dict.has_key(c)
            self.class_dict[c.value] = "pb" + filename

    def GetFixStrLen(self, field_type):
        return int(field_type[len(FIXSTR_TAG):])


def ValName(fieldname):
    valname = fieldname
    if fieldname.startswith("m_"):
        valname = fieldname[2:]
    return valname[0].upper() + valname[1:]


def FormatValNameList(val_list):
    line = "{"
    for v in val_list:
        if line == "{":
            line += "%s" % v
        else:
            line += ", %s" % v
    return line + "}"


def DumpFile(filename, erl_printer, hrl_printer):
    generator = ErlangGenerator(erl_printer, hrl_printer)
    parser = ProtoParser()
    input_file_path = os.path.abspath(filename)

    # 如果生成文件的更改时间晚于协议定义文件时间，则跳过此文件
    #output_file_name, output_file_path = cpp_generator.DetermineOuputPath(input_file_path)
    #if output_file_path != None:
    #    if os.stat(input_file_path).st_mtime < os.stat(output_file_path).st_mtime:
    # print("SKIPED %s" % input_file_path)
    #        return

    print("PROCESS %s" % input_file_path)
    parser.RegisterGenerator(generator)
    parser.ParseFile(input_file_path)
    generator.Generate(parser.tree, os.path.abspath(filename))


def GenerateHeader(erl_printer, module_name):
    erl_printer.AppendLine("%% This file was generator by proto_to_erl.py. DO NOT MODIFY MANNUAL.")
    erl_printer.AppendLine("")
    erl_printer.AppendLine('-module(%s).' % module_name)
    erl_printer.AppendLine("")
    erl_printer.AppendLine("-export([encode/2,encode/4,decode/2,decode/1]).")
    erl_printer.AppendLine("")
    erl_printer.AppendLine('-include("message_type.hrl\").')
    erl_printer.AppendLine('-include("protocol.hrl\").')
    erl_printer.AppendLine("""
-import(protocol_util, [decode_list/2, encode_list/2, 
                        encode_string/2, decode_string/1, decode_float/1]).

encode(Type, Uid, TimeStampMs, Data) ->
    <<Type:?UINT16, Uid:?UINT32, TimeStampMs:?UINT64,
     (serialize(encode, Type, Data))/binary>>.
encode(Type, Data) when is_atom(Type) ->
    serialize(encode, Type, Data);
encode(Type, Data) ->
    encode(Type, 0, 0, Data).

decode(Bin) ->
    <<MsgType:?UINT16, Uid:?UINT32, TimeStampMs:?UINT64,
        Bin1/binary>> = Bin,
    {Data, Bin2} = decode(MsgType, Bin1) ,
    {MsgType, {Uid, TimeStampMs}, Data, Bin2}.
decode(Type, Bin) ->
    serialize(decode, Type, Bin).
    """)
    erl_printer.AppendLine("")


def ErlAtom(name):
    if FIXSTR_TAG in name:
        name = "STRING"
    elif name in ["string", "float"]:
        name = name.upper()
    return "'%s'" % name


def GenerateTailor(erl_printer):
    erl_printer.AppendLine("""
serialize(decode, 'STRING', DATA) ->
    decode_string(DATA);
serialize(decode, 'FLOAT', DATA) ->
    decode_float(DATA);
serialize(encode, Type, Data) ->
    throw({encode_protocol_fail, Type, Data});
serialize(decode, Type, Data) ->
    throw({encode_protocol_fail, Type, Data}).
    """)


def DumpDirExt(file_ext, input_path,
               hrl_target_path, erl_target_path,
               func):
    filelist = []
    if os.path.isfile(input_path):
        filelist.append(input_path)
    elif os.path.isdir(input_path):
        filelist = glob.glob(input_path + "//*" + file_ext)
    assert len(filelist) > 0

    def mkdir(path):
        target_path = os.path.dirname(path)
        if not os.path.isdir(target_path):
            os.mkdir(target_path)

    mkdir(hrl_target_path)
    mkdir(erl_target_path)

    erl_printer = Printer(erl_target_path)
    hrl_printer = Printer(hrl_target_path)

    module_name = os.path.basename(os.path.splitext(erl_target_path)[0])
    GenerateHeader(erl_printer, module_name)

    for filename in filelist:
        func(filename, erl_printer, hrl_printer)

    GenerateTailor(erl_printer)

    erl_printer.Flush()
    hrl_printer.Flush()


def Main():
    start = time.time()
    print "Begin "
    assert len(sys.argv) >= 3, "usage: proto_to_erl.py INPUT HRLPATH ERLPATH"
    input_path = sys.argv[1]
    hrl_output_path = sys.argv[2]
    erl_output_path = sys.argv[3]

    DumpDirExt(".proto", input_path, hrl_output_path, erl_output_path, DumpFile)
    print "END. (used %f)." % (time.time() - start)

if __name__ == "__main__":
    Main()
    #RunProfile(Main)
        
    

