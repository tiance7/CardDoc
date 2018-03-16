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
    "INT32": ["number", "ReadInt32", "WriteInt32", True, False, 4, "0"],
    "int": ["number", "ReadInt32", "WriteInt32", True, False, 4, "0"],
    "int32": ["number", "ReadInt32", "WriteInt32", True, False, 4, "0"],
    "INT": ["number", "ReadInt32", "WriteInt32", True, False, 4, "0"],
    "CHAR": ["number", "ReadInt8", "WriteInt8", True, False, 1, "0"],
    "INT8": ["number", "ReadInt8", "WriteInt8", True, False, 1, "0"],
    "char": ["number", "ReadInt8", "WriteInt8", True, False, 1, "0"],
    "INT16": ["number", "ReadInt16", "WriteInt16", True, False, 2, "0"],
    "short": ["number", "ReadInt16", "WriteInt16", True, False, 2, "0"],
    "UINT16": ["number", "ReadUint16", "WriteUint16", True, False, 2, "0"],
    "BYTE": ["number", "ReadUint8", "WriteUint8", True, False, 1, "0"],
    "UINT8": ["number", "ReadUint8", "WriteUint8", True, False, 1, "0"],
    "UINT32": ["number", "ReadUint32", "WriteUint32", True, False, 4, "0"],
    "uint": ["number", "ReadUint32", "WriteUint32", True, False, 4, "0"],
    "float": ["number", "ReadFloat", "WriteFloat", True, False, 4, "0"],
    "FLOAT": ["number", "ReadFloat", "WriteFloat", True, False, 4, "0"],
    "string": ["string", "ReadString", "WriteString", True, False, 64, "''"],
    "INT64": ["uninet.Int64", "ReadInt64", "WriteInt64", True, False, 8, ""],
    "UINT64": ["uninet.Uint64", "ReadUint64", "WriteUint64", True, False, 8, ""],
    "ZGID": ["uninet.Uint64", "ReadUint64", "WriteUint64", True, False, 8, ""],
    "bool": ["boolean", "ReadUint8", "WriteUint8", True, False, 1, "false"],
    "Message": ["Message", "ReadMessage", "WriteMessage", True, True, 64, ""],
}


def CapFirstOnly(s):
    return s[0].upper() + s[1:]


class TsGenerator:
    """
    This class will transmit protocol-define file to  Actionscript source code.
    The Rule to Generate Js:
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
        self.default_size = 64;
        self.is_packet = False;

    def CamelCase(self, word):
        return ''.join(CapFirstOnly(x) for x in word.split('_'))

    def format_field_name(self, field, remove_prefix=True):
        """
        format the field name from m_nX, m_szUUU to its Camel Case
        :param field: the field name string
        :param remove_prefix: whether remove the prefix like m_n, m_sz
        :return: filed name in its Camel Case
        """
        name = field.strip()
        if name[:2] == "m_":
            name = name[2:]

        if remove_prefix:
            if (len(name) > 1 and name[0].islower() and name[1].isupper()) or (name[0:2] == "sz" and name[2].isupper()):
                matches = re.findall('([A-Z][\w-]*)', field.strip())
                if len(matches) > 0:
                    name = ''.join(matches[0:])

        return self.CamelCase(name)

    def determine_field_type(self, field_type):
        """
        Determine the filed type, for both simple type and class type
        :param field_type: field type name in string
        :return: the string represents the field type, for complex type, return as package.datatype .
        """
        import_package = self.need_import(field_type)
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
            self.class_set.add(node)

    def generate_packet_define(self, node):
        printer = self.FindPrinter(node)
        for c in self.cached_comments:
            printer.AppendLine(c)
            self.cached_comments = []
        printer.AppendLine("")

        printer.AppendLine("/// <reference path=\"../../dist/uninet.d.ts\" />")
        printer.AppendLine("")

        for field in node.childs:
            if field.token != "field_stmt":
                continue
            field_lable, field_type, field_name, field_index = field.value

            import_package = self.need_import(field_type)
            if import_package is not None:
                self.import_set.add('/// <reference path="../%s/%s.ts" />' % (import_package, field_type))
        if self.is_packet_type(node):
            printer.AppendLine("/// <reference path=\"../MessageType/MessageType.ts\" />")
        for _import in self.import_set:
            printer.AppendLine(_import)

        if len(self.import_set) > 0:
            printer.AppendLine("")
        self.import_set.clear()

        printer.AppendLine("module %s{" % self.package_name)
        printer.AppendLine("")
        printer.IncIndent()
        printer.AppendLine("export class %s{" % node.value)
        printer.IncIndent()

        if self.is_packet_type(node):
            printer.AppendLine("constructor(message:uninet.Message){")
            printer.IncIndent()
            printer.AppendLine("this.Message = message;")
            printer.DecIndent()
            printer.AppendLine("}")
            printer.AppendLine("")
            printer.AppendLine("Message: uninet.Message;")
        self.printer = printer

    def generate_decode_payload(self, node):
        if self.field_cnt == 0:
            return
        self.printer.AppendLine("Decode(stream:uninet.StreamBuffer) {")
        self.printer.IncIndent()
        member_count = 0
        for field in node.childs:
            if field.token != "field_stmt":
                continue

            member_count += 1
            field_lable, field_type, field_name, field_index = field.value
            if field_lable == "required":
                self.printer.AppendLine(self.determine_read_method(field_type, field_name))
            elif field_lable == "repeated":
                if 0 == self.repeated_cnt:
                    self.printer.AppendLine("var length:number;")
                self.repeated_cnt += 1
                self.printer.AppendLine("length = stream.ReadUint16();")
                self.printer.AppendLine("for (var i = 0; i < length; i++) {")
                self.printer.IncIndent()
                self.printer.AppendLine(self.determine_read_method(field_type, field_name, True))
                self.printer.DecIndent()
                self.printer.AppendLine("}")

        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def generate_encode_payload(self, node):
        if self.field_cnt == 0:
            return
        self.printer.AppendLine("Encode(stream:uninet.StreamBuffer) {")
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
                self.printer.AppendLine("stream.WriteUint16(this.%s.length);" % self.format_field_name(field_name))
                self.printer.AppendLine(
                    "for (var i = 0; i < this.%s.length; i++) {" % self.format_field_name(field_name))
                self.printer.IncIndent()
                self.printer.AppendLine(self.determine_write_method(field_type, field_name, True))
                self.printer.DecIndent()
                self.printer.AppendLine("}")
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def determine_write_method(self, field_type, field_name, is_vec=False):
        if self.is_enum_type(field_type):
            return "stream.WriteInt32(this.%s);" % self.format_field_name(field_name)
        elif self.is_class_type(field_type):
            if is_vec:
                return "this.%s[i].Encode(stream);" % self.format_field_name(field_name)
            else:
                return "this.%s.Encode(stream);" % self.format_field_name(field_name)
        elif field_type == "string" or field_type.startswith(FIXSTR_TAG):
            if is_vec:
                return "stream.WriteString(this.%s[i]);" % self.format_field_name(field_name)
            else:
                return "stream.WriteString(this.%s);" % self.format_field_name(field_name)
        elif g_type_dict.has_key(field_type):
            if is_vec:
                return "stream.%s(this.%s[i]);" % (g_type_dict[field_type][2], self.format_field_name(field_name))
            elif g_type_dict[field_type][4]:
                return "stream.%s(&this.%s);" % (g_type_dict[field_type][2], self.format_field_name(field_name))
            else:
                return "stream.%s(this.%s);" % (g_type_dict[field_type][2], self.format_field_name(field_name))

        raise SyntaxError, field_type

    def determine_read_method(self, field_type, field_name, is_vec=False):
        if self.is_enum_type(field_type):
            return "this.%s = stream.ReadInt32();" % self.format_field_name(field_name)
        elif self.is_class_type(field_type):
            if is_vec:
                return "this.%s.push(new %s()); \nthis.%s[this.%s.length-1].Decode(stream);" % (
                    self.format_field_name(field_name), self.determine_field_type(field_type),
                    self.format_field_name(field_name), self.format_field_name(field_name))
            else:
                return "this.%s = new %s(); \nthis.%s.Decode(stream);" % (
                    self.format_field_name(field_name), self.determine_field_type(field_type),
                    self.format_field_name(field_name))
        elif field_type == 'string' or field_type.startswith(FIXSTR_TAG):
            if is_vec:
                return "this.%s.push(stream.ReadString());" % self.format_field_name(field_name)
            else:
                return "this.%s = stream.ReadString();" % self.format_field_name(field_name)
        elif g_type_dict.has_key(field_type):
            if is_vec:
                return "this.%s.push(stream.%s());" % (self.format_field_name(field_name), g_type_dict[field_type][1])
            elif g_type_dict[field_type][3]:
                return "this.%s = stream.%s();" % (self.format_field_name(field_name), g_type_dict[field_type][1])
            else:
                return "this.%s = stream.%s();" % (self.format_field_name(field_name), g_type_dict[field_type][1])

        raise SyntaxError, field_type

    def is_packet_type(self, node):
        for child in node.childs:
            if child.token == "enum_stmt":
                if child.childs[0].value[0] == "THIS_MSG_TYPE":
                    self.MSG_TYPE = child.childs[0].value[1]
                    return True
        return False

    def generate_parse_packet(self, node):
        self.printer.AppendLine("export function Parse%s(msg:uninet.Message){" % (node.value))
        self.printer.IncIndent()
        self.printer.AppendLine("if (msg.Type() != MessageType.%s) {" % self.MSG_TYPE)
        self.printer.IncIndent()
        self.printer.AppendLine("return undefined;  ")
        self.printer.DecIndent()
        self.printer.AppendLine("}")
        self.printer.AppendLine("")
        self.printer.AppendLine("var pkt = new %s(msg);" % node.value)
        if self.field_cnt > 0:
            self.printer.AppendLine("var stream = new uninet.StreamBuffer(pkt.Message.Bytes);")
            self.printer.AppendLine("stream.Skip(uninet.MSG_HDR_LEN);")
            self.printer.AppendLine("pkt.Decode(stream);")
        self.printer.AppendLine("")
        self.printer.AppendLine("return pkt;")
        self.printer.DecIndent()
        self.printer.AppendLine("}")
        self.printer.AppendLine("")

        self.printer.AppendLine("export function New%s(%s) {" % (node.value, self.build_signature()))
        self.printer.IncIndent()
        self.printer.AppendLine("var pkt = new %s(new uninet.Message(0)); " % node.value)
        self.build_assignment(self.printer)
        self.printer.AppendLine("")
        self.printer.AppendLine("var buff = new uninet.StreamBuffer(%s.DEFAULT_SIZE);" % node.value)

        self.printer.AppendLine("buff.WriteHeader(pkt.Message.Header);")
        if self.field_cnt > 0:
            self.printer.AppendLine("pkt.Encode(buff);")
        self.printer.AppendLine("")
        self.printer.AppendLine("pkt.Message.Bytes = buff.Bytes();")
        self.printer.AppendLine("pkt.Message.SetType(MessageType.%s);" % self.MSG_TYPE)
        self.printer.AppendLine("pkt.Message.SetLen(buff.Len());")
        self.printer.AppendLine("")
        self.printer.AppendLine("return pkt;");
        self.printer.DecIndent()
        self.printer.AppendLine("}\n")

    def generate_consts_define(self, node, field_only=False):
        if len(self.const_set) == 0:
            return
        else:
            printer = self.FindPrinter(node)
            if not field_only:
                printer.AppendLine("")
                printer.AppendLine("/// const definition")
            # printer.IncIndent()
            for i in range(0, len(self.const_set)):
                if i + 1 < len(self.const_set) and self.const_set[i + 1][:2] == '//':
                    printer.AppendLine("%s  %s" % (self.const_set[i], self.const_set[i + 1]))
                elif not self.const_set[i][:2] == '//':
                    printer.AppendLine(self.const_set[i])
            # if not field_only:
            #     printer.DecIndent()
            #     printer.AppendLine(")")
            #     printer.AppendLine("")

            self.const_set = []

    def generate_message_define_end(self, node):
        printer = self.FindPrinter(node)
        self.generate_consts_define(node)
        printer.AppendLine("")
        self.generate_decode_payload(node)
        self.generate_encode_payload(node)

        printer.AppendLine("static DEFAULT_SIZE: number = %d;" % self.default_size)
        printer.AppendLine("")
        printer.DecIndent()
        printer.AppendLine("}")
        printer.AppendLine("")
        if self.is_packet_type(node):
            self.generate_parse_packet(node)

        # module close.
        printer.DecIndent()
        printer.AppendLine("}")
        printer.AppendLine("")

        self.repeated_cnt = 0
        self.field_cnt = 0
        self.fields = []

    def build_signature(self):
        sig = []

        for f in self.fields:
            sig.append("_%s:%s" % (f[0].lower(), f[1]))

        return ','.join(sig)

    def build_default_size(self):
        sizes = 16
        for f in self.fields:
            sizes += f[5]
        return sizes

    def build_assignment(self, printer):
        for f in self.fields:
            printer.AppendLine("pkt.%s =  _%s;" % (f[0], f[0].lower()))

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

    def get_ts_default(self, type_name):

        if g_type_dict.has_key(type_name):
            default_v = g_type_dict[type_name][6]
            if len(default_v) > 0:
                return " = %s" % g_type_dict[type_name][6]
        elif "number" == self.get_ts_name(type_name):
            return " = 0"
        elif "string" == self.get_ts_name(type_name):
            return " = ''"
        elif not self.is_packet:
            return " = new %s()" % self.get_ts_name(type_name)
        return " = undefined"

    def get_ts_name(self, type_name):
        if g_type_dict.has_key(type_name):
            return g_type_dict[type_name][0]

        if self.is_enum_type(type_name):
            return "number"

        if self.is_class_type(type_name):
            return self.determine_field_type(type_name)

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

    def need_import(self, type_name):
        for class_node in self.class_set:
            # print "class:", class_node.value
            if class_node.value == type_name:
                return self.find_package_name(class_node)
        return None

    def import_file(self, filename):
        import_file_path = os.path.join(self.input_dir, filename + ".proto")
        enum_set, class_set = FindCachedProtoTypes(import_file_path)
        self.enum_set.update(enum_set)
        self.class_set.update(class_set)

    def generate_field(self, node):
        self.field_cnt += 1
        field_lable = node.value[0]
        field_type = node.value[1]
        field_name = node.value[2]
        if not self.is_valid_type(field_type):
            print "TYPE: %s is not declared" % field_type
        else:
            import_package = self.need_import(field_type)
            if import_package is not None:
                pass
                # self.printer.AppendLine("import sixcube.%s.%s;" % \
                # (import_package, field_type))

        if field_lable != "repeated":
            self.printer.AppendLine("%s:%s%s; " % (self.format_field_name(field_name),
                                                   self.get_ts_name(field_type),
                                                   self.get_ts_default(field_type)))
            self.fields.append([self.format_field_name(field_name), self.get_ts_name(field_type)])
        else:
            self.printer.AppendLine(
                "%s:%s[] = [];" % (self.format_field_name(field_name), self.get_ts_name(field_type)))
            self.fields.append([self.format_field_name(field_name), "%s[]" % self.get_ts_name(field_type)])

        self.printer.sameLine = True

    def FindPrinter(self, node):
        filename = node.value + ".ts"
        file_full_path = "%s/%s/%s" % (self.outdir, self.package_name, filename)
        if not self.printerDict.has_key(file_full_path):
            printer = Printer(file_full_path)
            self.printerDict[file_full_path] = printer
            return printer
        else:
            return self.printerDict[file_full_path]

    def generate_enum_start(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)
            printer.AppendLine("// Generated by proto_to_ts.py , DO NOT EDIT!")
            printer.AppendLine("module %s{" % self.package_name)
            printer.IncIndent()
            printer.AppendLine("export enum %s{" % node.value)
            printer.IncIndent()

            self.printer = printer

    def generate_enum_define_end(self, node):
        if node.parent.token == "message_stmt":
            pass
        else:
            printer = self.FindPrinter(node)
            self.generate_consts_define(node, True)
            printer.DecIndent()
            printer.AppendLine("}")
            printer.DecIndent()
            printer.AppendLine("}")

    def GenerateEnumFieldStmt(self, node):
        if node.value[0] == "THIS_MSG_TYPE":
            pass
            # self.printer.AppendLine("%s int16 = MessageType.%s" % (node.value[0], node.value[1]))
        elif "message_stmt" in self.node_stack:
            self.const_set.append("static %s:number = %s;" % (node.value[0], node.value[1]))
        elif node.parent.token == "enum_stmt":
            self.const_set.append("%s = %s," % (node.value[0], node.value[1]))
        else:
            self.printer.AppendLine("var %s:number = %s;" % (node.value[0], node.value[1]))

    def BeginNode(self, node):
        self.node_stack.append(node.token)
        if node.token == "import_stmt":
            self.import_file(node.value)
        if node.token == "message_stmt":
            self.is_packet = self.is_packet_type(node)
            self.generate_packet_define(node)
        elif node.token == "field_stmt":
            self.generate_field(node)
        elif node.token == "enum_stmt":
            self.generate_enum_start(node)
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
            self.generate_message_define_end(node)
        elif node.token == "enum_stmt":
            self.generate_enum_define_end(node)
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
                   action="store", dest="prefix", default="",
                   help="prefix of package's full path")

    opt.add_option("-t", "--typeids",
                   action="store", dest="typeids", default="unitnet/packets",
                   help="import path for ids of packet type")

    (options, args) = opt.parse_args()

    if "" == options.define or "" == options.output or options.define is None:
        opt.print_help()
        sys.exit(1)

    def generate_proto(filename, target_dir, pkg_prefix, type_ids):
        ts_generator = TsGenerator(target_dir)
        parser = ProtoParser()
        parser.RegisterGenerator(ts_generator)
        print filename
        parser.ParseFile(os.path.abspath(filename))
        ts_generator.generate(parser.tree, os.path.abspath(filename), pkg_prefix, type_ids)

    start = time.time()
    print "Begin "
    DumpDirToGo(".proto", options.define, options.output, options.prefix, options.typeids, generate_proto)
    print "END. (used %f)." % (time.time() - start)
