#!/usr/bin/python

import sys
import re
from printer import Printer


def GetComment(line):
    what = re.compile(".*//(.*)").match(line)
    if what != None and len(what.groups()) > 0:
        return what.groups()[0]
    else:
        return ""


def Transform(filename, out):
    parsed = []
    lines = open(filename).readlines()

    printer = Printer(out)
    printer.AppendLine("package SystemErr")
    printer.AppendLine("")
    printer.AppendLine("// Generated by errinltogo.py. DO NOT EDIT!")
    printer.AppendLine("")
    printer.AppendLine("const ( // SystemErr")
    printer.IncIndent()

    re_declare = re.compile("ERR_MSG_DECLARE\((\S+),\s*(\d+),\s*\"(.+)\"\)")

    index = 0
    for line in lines:

        # prase assign state
        what = re_declare.match(line)
        if what is not None:
            msgName = what.groups()[0]
            assIndex = what.groups()[1]

            comment = what.groups()[2].decode("gbk", "ignore").encode('utf8')

            printer.AppendLine("%s int32 = %s    // %s"
                               % (msgName, assIndex, comment))

            index = int(assIndex)
            continue

        line = line.strip()
        if line.startswith("//") or len(line) == 0:
            printer.AppendLine("%s" % line.decode("gbk", "ignore").encode('utf8'))
        else:
            printer.AppendLine("// %s" % line.decode("gbk", "ignore").encode('utf8'))

    printer.DecIndent()
    printer.AppendLine(")")
    printer.AppendLine("")

    printer.Flush()


if __name__ == "__main__":
    """
    usage: inttoas.py INL_FILE OUT_FILE
    """
    input_path = sys.argv[1]
    output_path = None
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    Transform(input_path, output_path)
