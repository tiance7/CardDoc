#!/usr/bin/python
# -*- coding: gbk -*-

import time
import os
import sys, re
import optparse

from printer import Printer
from util import DumpDirToGo, RunProfile
from proto_parser import ProtoParser
from proto_handler import FindCachedProtoTypes
from const import FIXSTR_TAG


class IntType:
    def GetStoreType(self):
        return "int"

    def GetWriteMethod(self):
        return "%{stream_name}s.WriteInt(%{var_name}s)"


g_type_dict = {
    # defineType  langType  ReadFunc   WriteFunc  ReadAsPtr WriteAsPtr
    "INT32": ["int32", "ReadInt32", "WriteInt32", True, False],
    "int": ["int32", "ReadInt32", "WriteInt32", True, False],
    "INT": ["int32", "ReadInt32", "WriteInt32", True, False],
    "CHAR": ["int8", "ReadInt8", "WriteInt8", True, False],
    "INT8": ["int8", "ReadInt8", "WriteInt8", True, False],
    "char": ["int8", "ReadInt8", "WriteInt8", True, False],
    "INT16": ["int16", "ReadInt16", "WriteInt16", True, False],
    "short": ["int16", "ReadInt16", "WriteInt16", True, False],
    "UINT16": ["uint16", "ReadUint16", "WriteUint16", True, False],
    "BYTE": ["uint8", "ReadUint8", "WriteUint8", True, False],
    "UINT8": ["uint8", "ReadUint8", "WriteUint8", True, False],
    "UINT32": ["uint32", "ReadUint32", "WriteUint32", True, False],
    "uint": ["uint32", "ReadUint32", "WriteUint32", True, False],
    "float": ["float32", "ReadFloat", "WriteFloat", True, False],
    "FLOAT": ["float32", "ReadFloat", "WriteFloat", True, False],
    "string": ["string", "ReadString", "WriteString", True, False],
    "INT64": ["int64", "ReadInt64", "WriteInt64", True, False],
    "UINT64": ["uint64", "ReadUint64", "WriteUint64", True, False],
    "ZGID": ["uint64", "ReadUint64", "WriteUint64", True, False],
    "bool": ["bool", "ReadUint8", "WriteUint8", True, False],
    "Message": ["Message", "ReadMessage", "WriteMessage", True, True],
}


def CapFirstOnly(s):
    return s[0].upper() + s[1:]


class GoLangGenerator:
    """
    This class will transmit protocol-define file to  Actionscript source code.
    The Rule to Generate GoLang:
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
        self.MSG_TYPE = ""
        self.const_set = []
        self.repeated_cnt = 0
        self.import_set = set()
        self.field_cnt = 0
        self.fields = []
        self.package_prefix = ""
        self.type_ids = ""
        self.package_name = ""
        self.input_dir = ""

    def CamelCase(self, word):
        return ''.join(CapFirstOnly(x) for x in word.split('_'))

    def FormatName(self, field, remove_prefix=True):

        name = field.strip()
        if name[:2] == "m_":
            name = name[2:]

        if remove_prefix:
            if (len(name) > 1 and name[0].islower() and name[1].isupper()) or (name[0:2] == "sz" and name[2].isupper()):
                matches = re.findall('([A-Z][\w-]*)', field.strip())
                if len(matches) > 0:
                    name = ''.join(matches[0:])

        return self.CamelCase(name)

    def DetermineFieldType(self, field_type):
        import_package = self.DoNeedImport(field_type)
        if import_package is not None and import_package != self.package_name:
            return "%s.%s" % (import_package, field_type)
        elif g_type_dict.has_key(field_type):
            return g_type_dict[field_type][0]
        else:
            return field_type


    def OnAddNode(self, node):
        if node.token == "package":
            self.package_set.add(node)
        elif node.token == "enum_stmt":
            self.enum_set.add(node)
        elif node.token == "message_stmt":
            # print "add class node %s" % node.value
            self.class_set.add(node)

    def generate_packet_define(self, node):
        printer = self.FindPrinter(node)
        printer.AppendLine("package %s" % self.package_name)
        printer.AppendLine("")

        printer.AppendLine('import(')
        printer.IncIndent()
        # if self.is_packet_type(node):
        # printer.AppendLine('"bytes"')
        printer.AppendLine('"sixcube/types"')
        if self.is_packet_type(node):
            printer.AppendLine('"%s"' % (self.type_ids))

        for field in node.childs:
            if field.token != "field_stmt":
                continue
            field_lable, field_type, field_name, field_index = field.value

            import_package = self.DoNeedImport(field_type)
            if import_package is not None and import_package != self.package_name:
                self.import_set.add('"sixcube/%s/%s"' % (self.package_prefix, import_package))

        for _import in self.import_set:
            printer.AppendLine(_import)
        self.import_set.clear()

        printer.DecIndent()
        printer.AppendLine(')')

        printer.AppendLine("")
        for c in self.cached_comments:
            printer.AppendLine(c)
        self.cached_comments = []

        printer.AppendLine("type %s struct {" % node.value)
        printer.IncIndent()
        if self.is_packet_type(node):
            printer.AppendLine("*types.Message")
        self.printer = printer

    def generate_decode_payload(self, node):
        if self.field_cnt == 0:
            return
        self.printer.AppendLine("func (pkt *%s) Decode(stream *types.StreamBuffer) {" % node.value)
        self.printer.IncIndent()
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue

            memberCount += 1
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                self.printer.AppendLine(self.determine_read_method(field_type, field_name))
            elif field_lable == "repeated":
                if 0 == self.repeated_cnt:
                    self.printer.AppendLine("var length uint16")
                self.repeated_cnt += 1
                self.printer.AppendLine("stream.ReadUint16(&length)")
                self.printer.AppendLine(
                    "pkt.%s = make([]%s, length)" % (self.FormatName(field_name), self.DetermineFieldType(field_type)))
                self.printer.AppendLine("for i := uint16(0); i < length; i++ {")
                self.printer.IncIndent()
                self.printer.AppendLine(self.determine_read_method(field_type, field_name, True))
                self.printer.DecIndent()
                self.printer.AppendLine("}")

        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def determine_write_method(self, field_type, field_name, is_vec=False):
        if self.is_enum_type(field_type):
            return "stream.WriteUint32(pkt.%s)" % self.FormatName(field_name)
        elif self.is_class_type(field_type):
            if is_vec:
                return "pkt.%s[i].Encode(stream);" % self.FormatName(field_name)
            else:
                return "pkt.%s.Encode(stream);" % self.FormatName(field_name)
        elif field_type == "string" or field_type.startswith(FIXSTR_TAG):
            if is_vec:
                return "stream.WriteString(pkt.%s[i])" % self.FormatName(field_name)
            else:
                return "stream.WriteString(pkt.%s)" % self.FormatName(field_name)
        elif g_type_dict.has_key(field_type):
            if is_vec:
                return "stream.%s(pkt.%s[i])" % (g_type_dict[field_type][2], self.FormatName(field_name))
            elif g_type_dict[field_type][4]:
                return "stream.%s(&pkt.%s)" % (g_type_dict[field_type][2], self.FormatName(field_name))
            else:
                return "stream.%s(pkt.%s)" % (g_type_dict[field_type][2], self.FormatName(field_name))

        raise SyntaxError, field_type

    def determine_read_method(self, field_type, field_name, is_vec=False):
        if self.is_enum_type(field_type):
            return "stream.ReadUint32(&pkt.%s)" % self.FormatName(field_name)
        elif self.is_class_type(field_type):
            if is_vec:
                return "pkt.%s[i].Decode(stream);" % (self.FormatName(field_name))
            else:
                return "pkt.%s = %s{}; \npkt.%s.Decode(stream);" % (
                    self.FormatName(field_name), self.DetermineFieldType(field_type), self.FormatName(field_name))
        elif field_type == 'string' or field_type.startswith(FIXSTR_TAG):
            if is_vec:
                return "stream.ReadString(&pkt.%s[i])" % self.FormatName(field_name)
            else:
                return "stream.ReadString(&pkt.%s)" % self.FormatName(field_name)
        elif g_type_dict.has_key(field_type):
            if is_vec:
                return "stream.%s(&pkt.%s[i])" % (g_type_dict[field_type][1], self.FormatName(field_name))
            elif g_type_dict[field_type][3]:
                return "stream.%s(&pkt.%s)" % (g_type_dict[field_type][1], self.FormatName(field_name))
            else:
                return "stream.%s(pkt.%s)" % (g_type_dict[field_type][1], self.FormatName(field_name))

        raise SyntaxError, field_type

    def generate_encode_payload(self, node):
        if self.field_cnt == 0:
            return
        self.printer.AppendLine("func (pkt *%s) Encode(stream *types.StreamBuffer) {" % node.value)
        self.printer.IncIndent()
        memberCount = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue
            memberCount += 1
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                self.printer.AppendLine(self.determine_write_method(field_type, field_name))
            elif field_lable == "repeated":
                self.printer.AppendLine("stream.WriteUint16(uint16(len(pkt.%s)))" % self.FormatName(field_name))
                self.printer.AppendLine("for i, _ := range pkt.%s {" % self.FormatName(field_name))
                self.printer.IncIndent()
                self.printer.AppendLine(self.determine_write_method(field_type, field_name, True))
                self.printer.DecIndent()
                self.printer.AppendLine("}")
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def is_packet_type(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    self.MSG_TYPE = child.childs[0].value[1]
                    return True
        return False

    def generate_build_packet(self, node):

        self.printer.AppendLine("func Parse%s(msg *types.Message) *%s{" % (node.value, node.value))
        self.printer.IncIndent()
        self.printer.AppendLine("if msg.Msg != MessageType.%s {" % self.MSG_TYPE)
        self.printer.IncIndent()
        self.printer.AppendLine("return nil")
        self.printer.DecIndent()
        self.printer.AppendLine("}")
        self.printer.AppendLine("")
        self.printer.AppendLine("pkt := &%s{Message: msg}" % node.value)
        if self.field_cnt > 0:
            self.printer.AppendLine("stream := types.NewStreamBuffer(msg.Bytes[types.MSG_HDR_LEN:])")
            self.printer.AppendLine("pkt.Decode(stream)")
        self.printer.AppendLine("")
        self.printer.AppendLine("return pkt")
        self.printer.DecIndent()
        self.printer.AppendLine("}")
        self.printer.AppendLine("")

        self.printer.AppendLine("func New%s(cid uint32, %s) *%s {" % ( node.value, self.build_signature(), node.value))
        self.printer.IncIndent()

        self.printer.AppendLine("pkt := &%s{" % node.value)
        self.printer.IncIndent()
        self.printer.AppendLine("Message : &types.Message{Cid:cid},")
        self.build_assignment(self.printer)
        self.printer.DecIndent()
        self.printer.AppendLine("} ")

        self.printer.AppendLine(" ")
        self.printer.AppendLine("pkt.Msg = MessageType.%s" % self.MSG_TYPE)
        self.printer.AppendLine("")
        self.printer.AppendLine("buff := types.NewDefaultBuffer()")
        self.printer.AppendLine("buff.WriteHeader(&pkt.PacketHeader)")
        if self.field_cnt > 0:
            self.printer.AppendLine("pkt.Encode(buff)")
        self.printer.AppendLine("pkt.SetBuffer(buff)")
        self.printer.AppendLine("")
        # if self.field_cnt > 0:
        # self.printer.AppendLine("message := [...][]byte{header.Bytes(), payload.Bytes()}");
        # self.printer.AppendLine("pkt.Bytes = bytes.Join(message[:], nil)");
        # else:
        # self.printer.AppendLine("pkt.Bytes = header.Bytes()");

        self.printer.AppendLine("return pkt");
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")


    def GenerateConstsDef(self, node, field_only=False):
        if len(self.const_set) == 0:
            return
        else:
            printer = self.FindPrinter(node)
            if not field_only:
                printer.AppendLine("const (")
                printer.IncIndent()
            for i in range(0, len(self.const_set)):
                if i + 1 < len(self.const_set) and self.const_set[i + 1][:2] == '//':
                    printer.AppendLine("%s  %s" % (self.const_set[i], self.const_set[i + 1]))
                elif not self.const_set[i][:2] == '//':
                    printer.AppendLine(self.const_set[i])
            if not field_only:
                printer.DecIndent()
                printer.AppendLine(")")
                printer.AppendLine("")

            self.const_set = []


    def GenerateMessageDefEnd(self, node):
        printer = self.FindPrinter(node)
        printer.DecIndent()
        printer.AppendLine("}")
        printer.AppendLine("")
        self.GenerateConstsDef(node)
        self.generate_decode_payload(node)
        self.generate_encode_payload(node)
        if self.is_packet_type(node):
            self.generate_build_packet(node)
        self.repeated_cnt = 0
        self.field_cnt = 0
        self.fields = []

    def build_signature(self):
        sig = []

        for f in self.fields:
            sig.append("_%s %s" % (f[0].lower(), f[1]))

        return ','.join(sig)

    def build_assignment(self, printer):
        for f in self.fields:
            printer.AppendLine("%s : _%s," % (f[0], f[0].lower()))


    def is_enum_type(self, type_name):
        for enum in self.enum_set:
            # print "enum:", enum
            if enum.value == type_name:
                return True
        return False

    def is_class_type(self, type_name):
        for class_node in self.class_set:
            # print "class:", class_node.value
            if class_node.value == type_name:
                return True
        return False

    def get_as_type(self, type_name):
        if g_type_dict.has_key(type_name):
            return g_type_dict[type_name][0]

        if self.is_enum_type(type_name):
            return "uint32"

        if self.is_class_type(type_name):
            return self.DetermineFieldType(type_name)

        if type_name.startswith(FIXSTR_TAG):
            return "string"

        raise SyntaxError, type_name + self.printer.filename

    def is_valid_type(self, field_type):
        return True

    def find_package_name(self, node):
        while node.parent != None:
            node = node.parent
            if hasattr(node, "filename"):
                return os.path.basename(os.path.splitext(node.filename)[0])
        return None

    def DoNeedImport(self, type_name):
        for class_node in self.class_set:
            # print "class:", class_node.value
            if class_node.value == type_name:
                return self.find_package_name(class_node)
        return None

    def ImportFile(self, filename):
        import_file_path = os.path.join(self.input_dir, filename + ".proto")
        enum_set, class_set = FindCachedProtoTypes(import_file_path)
        self.enum_set.update(enum_set)
        self.class_set.update(class_set)

        # print self.class_set

    def GenerateField(self, node):
        self.field_cnt += 1
        field_lable = node.value[0]
        field_type = node.value[1]
        field_name = node.value[2]
        if not self.is_valid_type(field_type):
            print "TYPE: %s is not declared" % field_type
        else:
            import_package = self.DoNeedImport(field_type)
            if import_package is not None:
                pass
                # self.printer.AppendLine("import sixcube.%s.%s;" % \
                # (import_package, field_type))

        if field_lable != "repeated":
            self.printer.AppendLine("%s %s " % (self.FormatName(field_name), self.get_as_type(field_type)))
            self.fields.append([self.FormatName(field_name), self.get_as_type(field_type)])
        else:
            self.printer.AppendLine("%s []%s " % (self.FormatName(field_name), self.get_as_type(field_type)))
            self.fields.append([self.FormatName(field_name), "[]%s" % self.get_as_type(field_type)])

        self.printer.sameLine = True

    def FindPrinter(self, node):
        filename = node.value + ".go"
        file_full_path = "%s/%s/%s" % (self.outdir, self.package_name, filename)
        if not self.printerDict.has_key(file_full_path):
            printer = Printer(file_full_path)
            self.printerDict[file_full_path] = printer
            return printer
        else:
            return self.printerDict[file_full_path]

    def GenerateEnumStmt(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)
            printer.AppendLine("// Generated by proto_to_go.py. DO NOT EDIT!")
            printer.AppendLine("package %s" % self.package_name)
            printer.AppendLine("")
            printer.AppendLine("const(   // %s" % node.value)
            printer.IncIndent()
            printer.AppendLine("")

            self.printer = printer

    def GenerateEnumStmtEnd(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)
            self.GenerateConstsDef(node, True)
            printer.DecIndent()
            printer.AppendLine(")")


    def GenerateEnumFieldStmt(self, node):
        if node.value[0] == "THIS_MSG_TYPE":
            pass
            # self.printer.AppendLine("%s int16 = MessageType.%s" % (node.value[0], node.value[1]))
        elif "message_stmt" in self.node_stack:
            self.const_set.append("%s uint32 = %s" % (node.value[0], node.value[1]))
        elif node.parent.token == "enum_stmt":
            self.const_set.append("%s uint32 = %s" % (node.value[0], node.value[1]))
        else:
            self.printer.AppendLine("%s uint32 = %s" % (node.value[0], node.value[1]))

    def BeginNode(self, node):
        self.node_stack.append(node.token)
        if node.token == "import_stmt":
            self.ImportFile(node.value)
        if node.token == "message_stmt":
            self.generate_packet_define(node)
        elif node.token == "field_stmt":
            self.GenerateField(node)
        elif node.token == "enum_stmt":
            self.GenerateEnumStmt(node)
        elif node.token == "enum_field_stmt":
            self.GenerateEnumFieldStmt(node)
        elif node.token == "comment":
            text = node.value.decode('gbk', 'ignore').encode('utf8')
            if len(self.node_stack) == 0 or self.printer == None:
                self.cached_comments.append(text)
            elif node.parent.token == "enum_stmt":
                self.const_set.append(text)
            elif "message_stmt" not in self.node_stack:
                self.cached_comments.append(text)
            else:
                self.printer.AppendComment(text)

        return ""

    def EndNode(self, node):
        if node.token == "message_stmt":
            self.GenerateMessageDefEnd(node)
        elif node.token == "enum_stmt":
            self.GenerateEnumStmtEnd(node)
        self.node_stack.pop()
        return ""

    def generate(self, tree, input_file_path, pkg_prefix, type_ids):
        self.input_dir = os.path.dirname(input_file_path)
        self.package_name = os.path.basename(os.path.splitext(input_file_path)[0])
        self.package_prefix = pkg_prefix
        self.type_ids = type_ids

        tree.Apply(self)
        for printer in self.printerDict.values():
            printer.Flush()


if __name__ == "__main__":
    opt = optparse.OptionParser(usage="usage: %prog -d <proto directory> -o <output dir>[options] ")
    opt.add_option("-d", "--define",
                   dest="define", action="store",
                   help="defination file or directory", metavar="DEFINE")
    opt.add_option("-o", "--output",
                   action="store", dest="output", default="output",
                   help="output directory")
    opt.add_option("-p", "--prefix",
                   action="store", dest="prefix", default="unitnet/packets",
                   help="prefix of package's full path")

    opt.add_option("-t", "--typeids",
                   action="store", dest="typeids", default="unitnet/packets",
                   help="import path for ids of packet type")

(options, args) = opt.parse_args()

if "" == options.define or "" == options.output or options.define is None:
    opt.print_help()
    sys.exit(1)


def generate_proto(filename, target_dir, pkg_prefix, type_ids):
    go_generator = GoLangGenerator(target_dir)
    parser = ProtoParser()
    parser.RegisterGenerator(go_generator)
    print filename
    parser.ParseFile(os.path.abspath(filename))
    go_generator.generate(parser.tree, os.path.abspath(filename), pkg_prefix, type_ids)


start = time.time()
print "Begin "
DumpDirToGo(".proto", options.define, options.output, options.prefix, options.typeids, generate_proto)
print "END. (used %f)." % (time.time() - start)