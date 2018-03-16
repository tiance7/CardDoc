#!/usr/bin/python
# -*- coding: gbk -*-

import os
import sys
import glob
import logging

from printer import Printer
from util import DumpDir,IsNum
from cpp_parser import CppParser, EnumFieldNode
from grep_msg_type import LoadMatchesDict

class ProtoGenerator:
    """
            协议生成工具  此类读取C++语言生产协议定义的一个工具          
           此工具是为了兼容以前协议
    """
    def __init__(self):
        self.offset = 0
        self.type_list = []
        self.log = logging.getLogger('cpp2proto')
        self.message2typeDict = LoadMatchesDict("msg2type.txt")
        self.printer = Printer()
    
    def OnAddNode(self, node):
        pass

    def Generate(self, root, out_filename):
        root.Apply(self)
        self.printer.filename = out_filename
        self.log.debug(self.type_list)
        self.printer.Flush()
    
    def IsMyLenEnum(self, enum):
        if enum.value == "":
            return enum.childs[0].value[0] in ["MY_LEN", "MY_LENGTH", "THIS_LEN", "THIS_LENGTH"];
        return False
    
    def GenerateEnum(self, enum):
        if self.IsMyLenEnum(enum):
            return        
        self.printer.AppendLine('enum %s {' % enum.value)
        self.printer.IncIndent()
        
    def GetPrevEnum(self, node):
        index = node.parent.childs.index(node)
        r = range(0, index)
        r.reverse()                
        for i in r:
            child = node.parent.childs[i]
            if isinstance(child, EnumFieldNode):
                return child
        return None
    
    def GetEnumValue(self, enum_field):
        prev_enum = self.GetPrevEnum(enum_field) 
        if  prev_enum == None:        
            enum_field.enum_value = "0"            
        else:
            enum_exp = prev_enum.enum_name + " + 1"
            last_value = prev_enum.enum_value
            if IsNum(last_value):
                enum_exp = str(int(last_value) + 1)
            enum_field.enum_value = enum_exp
    
    def GenerateEnumField(self, enum_field):
        if self.IsMyLenEnum(enum_field.parent):
            return ""
                
        if enum_field.enum_value == None:
            #print enum_field.value
            enum_value = self.GetEnumValue(enum_field)
       
        self.printer.AppendLine("%s = %s;" % (enum_field.enum_name, enum_field.enum_value))
    
    def GenerateMessage(self, message):       
        if message.token == "class_stmt":
            self.printer.AppendLine('message %s {' % message.value)
            self.printer.IncIndent()
            # add a enum indicate message type
            self.printer.AppendLine("enum { THIS_MSG_TYPE = %s; }\n" % self.message2typeDict[message.value])
        else:
            self.printer.AppendLine('message %s {' % message.value)
            self.printer.IncIndent()        
    
    def GetLableAndType(self, field):
        if field.array_num == None:
            field_desc = field.member_type
            if 'std::vector<' in field_desc:
                return 'repeated', field_desc.replace('std::vector<', '').replace('>', '')
            elif 'std::string' == field_desc:
                return 'required', 'string'
            else:
                return 'required', field_desc
        else:
            if field.member_type != "char":            
                return 'repeated', field.member_type
            else:
                return 'required', 'string'
    
    def ComputeFieldIndex(self, field):
        index = 1
        for child in field.parent.childs:
            if child is field:
                return index
            if child.token == "member_data":
                index+=1
        assert False
    
    def GenerateField(self, field):
        index = self.ComputeFieldIndex(field) 
        if field.value[0] not in self.type_list:
            self.type_list.append(field.value[0])
        var_lable, var_type = self.GetLableAndType(field)                    
        self.printer.AppendLine('%s %s %s = %d;' % (var_lable, var_type, field.value[1], index)) 
    
    def GenerateComment(self, node):        
        index = node.parent.childs.index(node)
        if index > 0:
            sibling = node.parent.childs[index-1]
            if hasattr(sibling, "line_no"):
                if sibling.line_no == node.line_no:
                    self.printer.AppendSameLine("    %s" % node.value)    
                    return        
        self.printer.AppendLine("%s" % node.value)
        
    def BeginNode(self, node):
        if node.token in ['class_stmt', 'struct_stmt']: 
            self.GenerateMessage(node)
        elif node.token == 'member_data':
            self.GenerateField(node)
        elif node.token == 'enum_stmt':
            self.GenerateEnum(node)
        elif node.token == "enum_field_stmt":
            self.GenerateEnumField(node)
        elif node.token == "comment":
            self.GenerateComment(node)            
        else:
            self.log.debug("%s %s" % (node.token, node.value))
        return ''
    
    def EndNode(self, node):
        if node.token in ['class_stmt', 'struct_stmt']:
            self.printer.DecIndent()
            self.printer.AppendLine('}\n\n')
        elif node.token == 'enum_stmt':
            if self.IsMyLenEnum(node):
                return ""
            self.printer.DecIndent()
            self.printer.AppendLine('}\n\n')
        
        return ''

def usage():
    print "cpp_to_proto [input_dir] [output_dir]"
    print "cpp_to_proto [input_file] [output_dir]"

def DumpFile(filename, output_dir=None):
    generator = ProtoGenerator()
    parser = CppParser()
    parser.RegisterGenerator(generator)
    
    exclude_files = ["LogMessage.h", "PacketBase.h", "ManualMessage.h", "PersistMessage.h"]
    for f in exclude_files:
        if f in filename:
            print "LogMessage cannot be generator"
            return
    
         
    parser.ParseFile(os.path.abspath(filename))
    print parser.tree.Dump(0)
    
    def OutputFile(output_dir):
        if output_dir == None:
            return None
        else:
            basename = os.path.basename(os.path.splitext(filename)[0])
            basename += ".proto"
            output_filename = os.path.join(output_dir, basename)
            print "output file: ", output_filename
            return output_filename    
    generator.Generate(parser.tree, OutputFile(output_dir))
    

def RunTest():
    logging.basicConfig(level=logging.DEBUG,
                    format='[%(name)s,%(levelname)s]: %(message)s',
                    stream=sys.stderr)
    # DumpDir("..\\test\\cpp\\*.h", DumpFile)   
    DumpDir("test\\cpp\\test.h", DumpFile)
   
if __name__=="__main__":
    if len(sys.argv) == 1:
        RunTest()
        sys.exit()
        
    logging.basicConfig(level=logging.DEBUG,
                format='[%(name)s,%(levelname)s]: %(message)s',
                stream=sys.stderr)
    
    filelist = []
    if os.path.isfile(sys.argv[1]):
        filelist.append(sys.argv[1])
    elif os.path.isdir(sys.argv[1]):
        filelist = glob.glob(sys.argv[1]+"//*.h")
    assert len(filelist) > 0
    
    target_dir = sys.argv[2]
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)    
        #print "create directory failed"
       
    for filename in filelist:
        print "  File: %s" % os.path.abspath(filename)            
        DumpFile(filename, target_dir)
    