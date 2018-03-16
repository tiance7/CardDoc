#!/usr/bin/python
# -*- coding: gbk -*-

import sys
import time
import os
import os.path
from util import DumpDirExt
from const import FIXSTR_TAG
from printer import Printer
from proto_handler import FindCachedProtoTypes
from proto_parser import ProtoParser

"""
# cpp generator rule
# 01. We do not support nested class. All class will be declare in package namespace.
# 02. All enum will be declare in namespace, will no be declare in class.
# 
# Generate process
# 01. Find the dependency around Type
# 02. sort the class according the type
# 03. Generate
"""


class CppGenerator:
    def __init__(self, outdir):
        self.enum_list = set()
        self.class_list = []
        self.package_list = []
        self.has_namespace = False
        self.namespace_name = ''
        self.offset = 0
        self.printer = Printer()
        self.buildin_type = [
            "int", "char", "short", "UINT32", "INT32", "string", "std::string",
            "UINT16", "INT16", "BYTE", "ZGID", "bool", "float", "double",
            "UINT64", "INT64", "CHAR", "INT", "UINT8", "FLOAT"
        ]
        self.outdir = outdir

    def OnAddNode(self, node):
        if node.token == "package":
            self.package_list.append(node)
        elif node.token == "enum_stmt":
            self.enum_list.add(node)
        elif node.token == "message_stmt":
            self.class_list.append(node)

    def IsEnumType(self, type_name):
        for enum in self.enum_list:
            #print "enum:", enum
            if enum.value == type_name:
                return True
        return False

    def IsMessageType(self, type_name):
        for type in self.class_list:
            #print "enum:", enum
            if type.value == type_name:
                return True
        return False

    def IsValidType(self, type_name):
        if type_name in self.buildin_type:
            return True
        if self.IsEnumType(type_name):
            return True
        if self.IsMessageType(type_name):
            return True
        return False

    def GenerateCppHeader(self, filename):
        self.printer.AppendLine("// This file was generator by proto_to_cpp.py. DO NOT MODIFY MANNUAL.")
        self.printer.AppendLine("")
        self.printer.AppendLine("#ifndef __%s__" % filename.replace('.', '_').upper())
        self.printer.AppendLine("#define __%s__" % filename.replace('.', '_').upper())
        self.printer.AppendLine("")
        self.printer.AppendLine("#include <net/PacketBase.h>")
        self.printer.AppendLine("")

    def GenerateCppTailor(self, filename):
        self.printer.AppendLine("#endif // %s\n" % filename.replace('.', '_').upper())

    def DetermineOuputPath(self, input_file_path):
        basename = os.path.basename(os.path.splitext(input_file_path)[0])
        output_file_name = basename + ".pb.h"
        if self.outdir != None:
            output_file_path = os.path.join(self.outdir, output_file_name)
        else:
            output_file_path = None
        return output_file_name, output_file_path

    def Generate(self, tree, input_file_path):
        if self.outdir != None and not os.path.exists(self.outdir):
            os.mkdir(self.outdir)

        self.input_dir = os.path.dirname(input_file_path)

        output_file_name, output_file_path = self.DetermineOuputPath(input_file_path)

        self.printer = Printer(output_file_path)
        self.GenerateCppHeader(output_file_name)
        s = tree.Apply(self)
        if self.has_namespace:
            s = "namespace %s {\n\n%s}" % (self.namespace_name, s)
        self.GenerateCppTailor(output_file_name)
        self.printer.Flush()

    def GetParamType(self, var_type):
        """
        Convert parameter type to C++ type.
        now there are two rules:
        1. All build-in type pass by value, otherwise pass by refrence.
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

    def GenerateReadConstructor(self, node):
        self.printer.AppendLine("/// constructor ")
        self.printer.AppendLine("explicit %s(NetMessage* pMsg)" % node.value)
        self.printer.AppendLine(": PacketBase(pMsg)")
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        self.printer.AppendLine("GetStream() >> *this;")
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")
        return ''

    def GenerateReadFromStream(self, node):
        self.printer.AppendLine("/// overload operator>>, read from stream ")
        self.printer.AppendLine("friend NetMessage& operator>>(NetMessage& inputStream,  %s& v)" % node.value)
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        memberCount = 0
        for child in node.childs:
            if child.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = child.value
            if field_lable == "required":
                if self.IsEnumType(field_type):
                    self.printer.AppendLine("v.%s = static_cast<%s>(inputStream.ReadD());" \
                                            % (field_name, field_type))
                elif FIXSTR_TAG in field_type:
                    self.printer.AppendLine("{");
                    self.printer.IncIndent()
                    self.printer.AppendLine("size_t n = inputStream.ReadH();")
                    self.printer.AppendLine("if (n >= sizeof(v.%s)) { n = sizeof(v.%s); } else { v.%s[n] = '\\0'; }" % (
                    field_name, field_name, field_name))
                    self.printer.AppendLine("for (size_t i = 0; i < n; ++i) { inputStream >> v.%s[i]; };" % field_name)
                    self.printer.DecIndent()
                    self.printer.AppendLine("}");
                else:
                    self.printer.AppendLine("inputStream >> v.%s;" % field_name)
            elif field_lable == "repeated":
                self.printer.AppendLine("{")
                self.printer.IncIndent()
                self.printer.AppendLine("size_t n = inputStream.ReadH();")
                self.printer.AppendLine("v.%s.resize(n);" % field_name);
                self.printer.AppendLine("for (size_t i = 0; i < n; ++i) { inputStream >> v.%s[i]; };" % field_name)
                self.printer.DecIndent()
                self.printer.AppendLine("}")
        if memberCount == 0:
            self.printer.AppendLine("UNUSED_ARG(v);")
        self.printer.AppendLine("return inputStream;")
        self.printer.DecIndent()
        self.printer.AppendLine("}")

    def GenerateWriteConstructor(self, node):
        # Constructor from data
        result = ""
        para_list = ""
        init_list = ""
        for child in node.childs:
            if child.token != "field_stmt":
                continue
            para_list += (", " + self.GeneratePara(child))
            init_list += ", %s(%s)" % (child.value[2], self.GetParamName(child.value[2]))
        para_list = "ClientId cid" + para_list

        #参数列表
        self.printer.AppendLine("/// constructor ")
        self.printer.AppendLine("%s(%s)" % (node.value, para_list))
        # 基类初始化
        self.printer.AppendLine(": PacketBase(THIS_MSG_TYPE, cid, DEFAULT_PACKET_SIZE)")
        # 类初始化类表
        if init_list != "":
            self.printer.AppendLine("%s" % init_list)
        self.printer.AppendLine("{")
        self.printer.IncIndent()

        self.printer.AppendLine("GetStream() << *this;")

        self.printer.DecIndent()
        self.printer.AppendLine("}\n")
        return result
        
    def GenerateRewirteStream(self, node):
        #参数列表
        self.printer.AppendLine("/// rewrite to stream  ")
        self.printer.AppendLine("void RewirteToStream()")
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        
        self.printer.AppendLine("if (m_pMsg) DestroyMessage(m_pMsg); \n")
        self.printer.AppendLine("m_pMsg = new NetMessage(DEFAULT_PACKET_SIZE + HDR_LEN, THIS_MSG_TYPE, 0);")
        self.printer.AppendLine("GetStream() << *this;")

        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def GenerateSimpleConstructor(self, node):
        # Constructor from data
        result = ""
        para_list = ""
        init_list = ""
        null_init_list = ""
        assign_list = []
        null_assign_list = []
        for child in node.childs:
            if child.token != "field_stmt":
                continue
            if para_list != "":
                para_list += ", "
            para_list += self.GeneratePara(child)

            var_lable, var_type, var_name = child.value[0:3]

            if FIXSTR_TAG in var_type:
                assign_list.append("strncpy(%s, %s.c_str(), sizeof(%s));" \
                                   % (var_name, self.GetParamName(var_name), var_name));
                null_assign_list.append("memset(%s, 0, sizeof(%s));" % (var_name, var_name));
                continue

            if init_list != "":
                init_list += ", "
                null_init_list += ", "

            init_list += "%s(%s)" % (var_name, self.GetParamName(var_name))
            null_init_list += "%s()" % var_name

        #参数列表
        self.printer.AppendLine("/// constructor ")
        self.printer.AppendLine("%s(%s)" % (node.value, para_list))
        # 基类初始化        
        # 类初始化类表
        if init_list != "":
            self.printer.AppendLine(": %s" % init_list)
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        for line in assign_list: self.printer.AppendLine(line)
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

        # default constrctor
        self.printer.AppendLine("/// default consturctor")
        self.printer.AppendLine("%s()" % node.value)
        if null_init_list != "":
            self.printer.AppendLine(": %s" % null_init_list)
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        for line in null_assign_list: self.printer.AppendLine(line)
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")
        return result

    def GenerateWriteToStream(self, node):
        self.printer.AppendLine("/// overload operator<<, write to stream ")
        self.printer.AppendLine("friend NetMessage& operator<<(NetMessage& outputStream, %s& v)" % node.value)
        self.printer.AppendLine("{")
        self.printer.IncIndent()
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                if self.IsEnumType(field_type):
                    self.printer.AppendLine("outputStream << static_cast<int>(v.%s);" % field_name)
                elif FIXSTR_TAG in field_type:
                    self.printer.AppendLine("outputStream << static_cast<UINT16>(sizeof(v.%s));" % field_name);
                    self.printer.AppendLine("for(size_t i = 0; i < sizeof(v.%s);++i) { outputStream << v.%s[i];}" \
                                            % (field_name, field_name))
                else:
                    self.printer.AppendLine("outputStream << v.%s;" % field_name)
            elif field_lable == "repeated":
                self.printer.AppendLine("outputStream << static_cast<UINT16>(v.%s.size());" % field_name)
                self.printer.AppendLine("for(size_t i = 0; i < v.%s.size(); ++i) { outputStream << v.%s[i]; }" \
                                        % (field_name, field_name))
        if memberCount == 0:
            self.printer.AppendLine("UNUSED_ARG(v);")
        self.printer.AppendLine("return outputStream;")
        self.printer.DecIndent()
        self.printer.AppendLine("}")

    def NeedConstructor(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    return True
        return False

    def GenerateMessageDef(self, node):
        if self.NeedConstructor(node):
            self.printer.AppendLine("class %s : public PacketBase" % (node.value))
        else:
            self.printer.AppendLine("class %s" % (node.value))
        self.printer.AppendLine("{")
        self.printer.AppendLine("public:")
        self.printer.IncIndent()
        # Constructor from Message

    def GenerateMessageMethod(self, node):
        if self.NeedConstructor(node):
            self.GenerateReadConstructor(node)
            self.GenerateWriteConstructor(node)
            self.GenerateRewirteStream(node)
        else:
            self.GenerateSimpleConstructor(node)
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
        self.class_list += class_list

    def BeginNode(self, node):
        result = ''
        if node.token == "import_stmt":
            self.ImportFile(node.value)
            self.printer.AppendLine("#include \"%s.pb.h\"" % node.value)
        elif node.token == "package_stmt":
            self.namespace_name = node.value
            self.has_namespace = True
        elif node.token == "enum_stmt":
            if node.value == "unnamed":
                self.printer.AppendLine("enum {")
            else:
                self.printer.AppendLine("enum %s {" % (node.value))
            self.printer.IncIndent()
        elif node.token == "enum_field_stmt":
            self.printer.AppendLine("%s = %s," % (node.value[0], node.value[1]))
            self.printer.sameLine = True
        elif node.token == "comment":
            self.printer.AppendComment(node.value)
        elif node.token in ["root", "option_stmt"]:
            pass
        elif node.token == "message_stmt":
            self.GenerateMessageDef(node)
        elif node.token == "struct_stmt":
            self.printer.AppendLine("struct %s {" % (node.value))
            self.printer.IncIndent()
        elif node.token == "struct_field_stmt":
            if len(node.value) == 2:
                self.printer.AppendLine("%s %s;\n" % (node.value[0], node.value[1]))
            else:
                self.printer.AppendLine("%s %s[%s];\n" % (node.value[0], node.value[1], node.value[2]))
            self.printer.sameLine = True
        elif node.token == "field_stmt":
            #print node.value
            field_lable = node.value[0]
            field_type = node.value[1]
            field_name = node.value[2]
            if not self.IsValidType(field_type):
                print "TYPE: %s is not declared" % field_type

            if field_lable != "repeated":
                if FIXSTR_TAG not in field_type:
                    self.printer.AppendLine(("%s %s;" % (self.GetCppType(field_type), field_name)))
                else:
                    self.printer.AppendLine("char %s[%d];" % (field_name, self.GetFixStrLen(field_type)))
            else:
                assert FIXSTR_TAG not in field_type
                self.printer.AppendLine("std::vector<%s> %s;" % (self.GetCppType(field_type), field_name))
            self.printer.sameLine = True
        else:
            print node.token
        return result

    def GetFixStrLen(self, field_type):
        return int(field_type[len(FIXSTR_TAG):])

    def EndNode(self, node):
        if node.token == "enum_stmt":
            self.printer.DecIndent()
            self.printer.AppendLine("};\n")
        elif node.token in ["message_stmt", "struct_stmt"]:
            self.GenerateMessageMethod(node)
            self.printer.DecIndent()
            self.printer.AppendLine("};\n")
        return ''


def Main():
    def DumpFile(filename, targetDir):
        cpp_generator = CppGenerator(targetDir)
        parser = ProtoParser()
        input_file_path = os.path.abspath(filename)

        # 如果生成文件的更改时间晚于协议定义文件时间，则跳过此文件
        #output_file_name, output_file_path = cpp_generator.DetermineOuputPath(input_file_path)
        #if output_file_path != None:
        #    if os.stat(input_file_path).st_mtime < os.stat(output_file_path).st_mtime:
        # print("SKIPED %s" % input_file_path)
        #        return
        print("PROCESS %s" % input_file_path)
        parser.RegisterGenerator(cpp_generator)
        parser.ParseFile(input_file_path)
        cpp_generator.Generate(parser.tree, os.path.abspath(filename))

    start = time.time()
    print "Begin "
    DumpDirExt(".proto", sys.argv[1], sys.argv[2], DumpFile)
    print "END. (used %f)." % (time.time() - start)


if __name__ == "__main__":
    Main()
    #RunProfile(Main)
        
    
