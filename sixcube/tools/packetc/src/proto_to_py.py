#!/usr/bin/python
# -*- coding: gbk -*-

import time
import os
import sys
from printer import Printer
from util import DumpDirExt, RunProfile
from proto_parser import ProtoParser
from proto_handler import FindCachedProtoTypes
from const import FIXSTR_TAG

class IntType:
    def GetStoreType(self):
        return "int"

    def GetWriteMethod(self):
        return "%{stream_name}s.WriteInt(%{var_name}s)"

g_type_dict = {
    "INT32": ["int", "readInt", "writeInt"],
    "int": ["int", "readInt", "writeInt"],
    "INT": ["int", "readInt", "writeInt"],
    "CHAR": ["int", "readByte", "writeByte"],
    "char": ["int", "readByte", "writeByte"],
    "INT16": ["int", "readShort", "writeShort"],
    "short": ["int", "readShort", "writeShort"],
    "UINT16": ["uint", "readUnsignedShort", "writeShort"],
    "BYTE": ["uint", "readUnsignedByte", "writeByte"],
    "UINT8": ["uint", "readUnsignedByte", "writeByte"],
    "UINT32": ["uint", "readUnsignedInt", "writeUnsignedInt"],
    "uint": ["uint", "readUnsignedInt", "writeUnsignedInt"],
    "float": ["Number", "readFloat", "writeFloat"],
    "FLOAT": ["Number", "readFloat", "writeFloat"],
    "string": ["String", "Utf-8", "Utf-8"],
    "INT64": ["INT64", "double", "double"],
    "UINT64": ["UINT64", "double", "double"],
    "ZGID": ["UINT64", "double", "double"],
    "bool": ["Boolean", "readByte", "writeByte"],
}

def ToPythonComment(c):
    return "#" + c.replace("\n", "\n#")


class ActionScriptGenerator:
    """
    This class will transmit protocol-define file to  Actionscript source code.
    The Rule to Generate ActionScript:
    1. Every proto-file will be a package.
    2. Every message will be an action script class.
    3. Every enum will be a enum class.    
    4. We need do some stastics.
    """

    def __init__(self, outdir):
        self.outdir = outdir
        self.printerDict = {}
        self.enum_set = set()
        self.class_set = set()
        self.package_set = set()
        self.node_stack = []
        self.cached_comments = []
        self.printer = None

    def OnAddNode(self, node):
        if node.token == "package":
            self.package_set.add(node)
        elif node.token == "enum_stmt":
            self.enum_set.add(node)
        elif node.token == "message_stmt":
            #print "add class node %s" % node.value
            self.class_set.add(node)

    def GenerateMessageDef(self, node):
        printer = self.FindPrinter(node)
        # printer.AppendLine("package %s" % self.package_prefix)
        # printer.AppendLine("{")
        # printer.IncIndent()
        # printer.AppendLine("import flash.utils.ByteArray;")        
        printer.AppendLine("")
        for c in self.cached_comments:
            printer.AppendLine(ToPythonComment(c))
        self.cached_comments = []
        printer.AppendLine("class %s:" % node.value)
        printer.IncIndent()
        self.printer = printer

    def GenerateReadFromStream(self, node):
        self.printer.AppendLine("def readFromStream(self, stream):")
        self.printer.IncIndent()
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            memberCount += 1
            # print field.value
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                self.printer.AppendLine(self.DetermineReadMethod(field_type, "self.%s" % field_name))
            elif field_lable == "repeated":
                self.printer.AppendLine("%s = [];" % field_name)
                self.printer.AppendLine("for i in range(stream.readUnsignedShort()):")
                self.printer.IncIndent()
                self.printer.AppendLine("self.%s[i].append(None)" % field_name)
                self.printer.AppendLine(self.DetermineReadMethod(field_type, "self.%s[i]" % field_name))
                self.printer.DecIndent()

        self.printer.DecIndent()
        self.printer.AppendLine("")

    def DetermineWriteMethod(self, field_type, field_name):
        if self.IsEnumType(field_type):
            return "stream.writeInt(%s);" % field_name
        elif self.IsClassType(field_type):
            return "%s.writeToStream(stream);" % field_name
        elif field_type == "string" or field_type.startswith(FIXSTR_TAG):
            return "stream.writeUTF(%s);" % field_name
        elif field_type == "INT64":
            return "stream.writeUnsignedInt(%s.lowpart); stream.writeInt(%s.hipart);" % (field_name, field_name)
        elif field_type in ["UINT64", "ZGID"]:
            return "stream.writeUnsignedInt(%s.lowpart); stream.writeUnsignedInt(%s.hipart);" % (field_name, field_name)
        elif g_type_dict.has_key(field_type):
            return "stream.%s(%s);" % (g_type_dict[field_type][2], field_name)

        raise SyntaxError, field_type

    def DetermineReadMethod(self, field_type, field_name):
        if self.IsEnumType(field_type):
            return "%s = stream.readInt();" % field_name
        elif self.IsClassType(field_type):
            return "%s = %s(); %s.readFromStream(stream);" % (field_name, field_type, field_name)
        elif field_type == 'string' or field_type.startswith(FIXSTR_TAG):
            return "%s = stream.readUTF();" % field_name
        elif field_type == 'INT64':
            return "%s = stream.readInt64()" % field_name
        elif field_type in ["UINT64", "ZGID"]:
            return "%s = stream.readUInt64()" % field_name
        elif g_type_dict.has_key(field_type):
            return "%s = stream.%s();" % (field_name, g_type_dict[field_type][1])
        raise SyntaxError, field_type

    def GenerateWriteToStream(self, node):
        self.printer.AppendLine("def writeToStream(self, stream):")
        self.printer.IncIndent()
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                self.printer.AppendLine(self.DetermineWriteMethod(field_type, "self.%s" % field_name))
            elif field_lable == "repeated":
                self.printer.AppendLine("stream.writeShort(len(self.%s));" % field_name)
                self.printer.AppendLine("for item in self.%s:" % field_name)
                self.printer.IncIndent()
                self.printer.AppendLine(self.DetermineWriteMethod(field_type, "item"))
                self.printer.DecIndent()
        self.printer.DecIndent()
        self.printer.AppendLine("")

    def NeedConstructor(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    return True
        return False

    def GenerateBuildPacket(self, node):
        self.printer.AppendLine("def buildPacket(self):")
        self.printer.IncIndent()
        self.printer.AppendLine("abuff = ProtocolBuffer.NewBuffer();")
        self.printer.AppendLine("abuff.writeShort(self.__class__.THIS_MSG_TYPE);");
        self.printer.AppendLine("abuff.writeUnsignedInt(0);");
        self.printer.AppendLine("abuff.writeUnsignedInt(0);");
        self.printer.AppendLine("abuff.writeUnsignedInt(0);");
        self.printer.AppendLine("self.writeToStream(abuff);")
        self.printer.AppendLine("return abuff;")
        self.printer.DecIndent()

    def GetDefaultValue(self, label, typename):
        if label == "repeated":
            return "[]"
        elif typename == "string":
            return '""'
        elif typename in ["FLOAT", "INT", "INT64", "UINT16", "INT16", "int", "ZGID", "float", "UINT32", "BYTE", "bool",
                          "INT32", "UINT64"]:
            return 0
        elif self.IsEnumType(typename):
            return 0
        else:
            return "%s()" % typename

    def GenerateConstructor(self, node):
        # Constructor from data
        result = ""
        init_list = []
        for child in node.childs:
            if child.token != "field_stmt":
                continue
                # print child.value
            label = child.value[0]
            typename = child.value[1]
            name = child.value[2]
            init_list.append("self.%s = %s" % (name, self.GetDefaultValue(label, typename)))

        #参数列表
        self.printer.AppendLine("# constructor ")
        self.printer.AppendLine("def __init__(self):")
        self.printer.IncIndent()

        # 类初始化类表
        for item in init_list:
            self.printer.AppendLine(item)

        self.printer.DecIndent()
        self.printer.AppendLine("")
        return result

    def GenerateMessageDefEnd(self, node):
        self.GenerateReadFromStream(node)
        self.GenerateWriteToStream(node)
        if self.NeedConstructor(node):
            self.GenerateConstructor(node)
            self.GenerateBuildPacket(node)
        printer = self.FindPrinter(node)
        printer.DecIndent()


    def IsEnumType(self, type_name):
        for enum in self.enum_set:
            #print "enum:", enum
            if enum.value == type_name:
                return True
        return False

    def IsClassType(self, type_name):
        for class_node in self.class_set:
            #print "class:", class_node.value
            if class_node.value == type_name:
                return True
        return False

    def GetAsType(self, type_name):
        if g_type_dict.has_key(type_name):
            return g_type_dict[type_name][0]

        if self.IsEnumType(type_name):
            return "int"

        if self.IsClassType(type_name):
            return type_name

        if type_name.startswith(FIXSTR_TAG):
            return "String"

        raise SyntaxError, type_name + self.printer.filename

    def IsValidType(self, field_type):
        return True

    def FindPackageName(self, node):
        while node.parent != None:
            node = node.parent
            if hasattr(node, "filename"):
                return os.path.basename(os.path.splitext(node.filename)[0])
        return None

    def DoNeedImport(self, type_name):
        for class_node in self.class_set:
            #print "class:", class_node.value
            if class_node.value == type_name:
                return self.FindPackageName(class_node)
        return None

    def ImportFile(self, filename):
        import_file_path = os.path.join(self.input_dir, filename + ".proto")
        enum_set, class_set = FindCachedProtoTypes(import_file_path)
        self.enum_set.update(enum_set)
        self.class_set.update(class_set)
        #print self.class_set

    def GenerateField(self, node):
        field_lable = node.value[0]
        field_type = node.value[1]
        field_name = node.value[2]
        if not self.IsValidType(field_type):
            print "TYPE: %s is not declared" % field_type
        else:
            import_package = self.DoNeedImport(field_type)
            if import_package != None:
                self.printer.AppendLine("from onwind.protocol.%s import %s " %\
                                        (import_package, field_type))

        if field_lable != "repeated":
            #self.printer.AppendLine("public var %s:%s;" % \
            #                        (field_name, self.GetAsType(field_type)))
            pass
        else:
            #self.printer.AppendLine("public var %s:Array; /* array of %s */" % (field_name, field_type))
            pass

    def FindPrinter(self, node):
        #filename = node.value + ".py"
        file_full_path = "%s/onwind/protocol/%s.py" % (self.outdir, self.package_name)
        if not self.printerDict.has_key(file_full_path):
            printer = Printer(file_full_path)
            self.printerDict[file_full_path] = printer
            printer.AppendLine("# -*- coding: gbk -*-")
            printer.AppendLine("import onwind.net.ProtocolBuffer as ProtocolBuffer")
            printer.AppendLine("import onwind.protocol.MessageType as MessageType")
            return printer
        else:
            return self.printerDict[file_full_path]

    def GenerateEnumStmt(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)
            printer.AppendLine("# Generated by proto_to_as.py. DO NOT EDIT!")
            printer.AppendLine("")
            self.printer = printer

    def GenerateEnumStmtEnd(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)

    def GenerateEnumFieldStmt(self, node):
        if node.value[0] == "THIS_MSG_TYPE":
            self.printer.AppendLine("%s = MessageType.%s" % (node.value[0], node.value[1]))
        else:
            self.printer.AppendLine("%s = %s" % (node.value[0], node.value[1]))

    def BeginNode(self, node):
        self.node_stack.append(node.token)
        if node.token == "import_stmt":
            self.ImportFile(node.value)
        if node.token == "message_stmt":
            self.GenerateMessageDef(node)
        elif node.token == "field_stmt":
            self.GenerateField(node)
        elif node.token == "enum_stmt":
            self.GenerateEnumStmt(node)
        elif node.token == "enum_field_stmt":
            self.GenerateEnumFieldStmt(node)
        elif node.token == "comment":
            if len(self.node_stack) == 0 or\
               self.printer == None or\
               "message_stmt" not in self.node_stack:
                self.cached_comments.append(node.value)
            else:
                self.printer.AppendLine(node.value)

        return ""

    def EndNode(self, node):
        if node.token == "message_stmt":
            self.GenerateMessageDefEnd(node)
        elif node.token == "enum_stmt":
            self.GenerateEnumStmtEnd(node)
        self.node_stack.pop()
        return ""

    def Generate(self, tree, input_file_path):
        self.input_dir = os.path.dirname(input_file_path)
        self.package_name = os.path.basename(os.path.splitext(input_file_path)[0])
        self.full_qualified_package_name = "onwind.protocol." + self.package_name
        tree.Apply(self)
        for printer in self.printerDict.values():
            printer.Flush()


def Main():
    input_path = "../proto_out"
    output_path = "../py_out"
    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_path = sys.argv[2]

    def DumpFile(filename, targetDir):
        cpp_generator = ActionScriptGenerator(targetDir)
        parser = ProtoParser()
        parser.RegisterGenerator(cpp_generator)
        print filename
        parser.ParseFile(os.path.abspath(filename))
        cpp_generator.Generate(parser.tree, os.path.abspath(filename))

    start = time.time()
    print "Begin "
    DumpDirExt(".proto", input_path, output_path, DumpFile)
    print "END. (used %f)." % (time.time() - start)

if __name__ == "__main__":
    #RunProfile(Main)
    Main()
