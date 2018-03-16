#!/usr/bin/env python
import os, os.path, sys, optparse

#import bundled MakoTemplates module
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))

from mako.runtime import Context
from mako.template import Template

cur_dir = os.path.dirname(sys.argv[0])

if __name__ == '__main__':

    parser = optparse.OptionParser(usage="usage: %prog [options] <file>.xml | <dir> ")
    parser.add_option("-d", "--directory", dest="directory", action="store", default=".",
                      help="defination directory", metavar="DIRECTORY")
    parser.add_option("-o", "--output", action="store", dest="output", default=".",
                      help="output directory")
    parser.add_option("-p", "--prefix", action="store", dest="prefix", default="entity",
                      help="prefix of the package")

    (options, args) = parser.parse_args()

    print "Generating PersistMain.cpp ...",

    OBJECTS = []
    for dir_path, dir_names, file_names in os.walk(options.directory):
        for file_name in file_names:
            base, ext = os.path.splitext(file_name)
            if ext == ".h" and base != "stdafx" and base != "DaoObject" and base != "DaoProxy" and base != "DaoIds":
                dir_path = dir_path.replace(".\\", "").replace(".", "")
                OBJECTS.append([base, os.path.join(dir_path, file_name).replace("\\", "/")])

    template = Template(filename=os.path.join(cur_dir, "templates/PersistMain_cpp.mako"))

    output = file(os.path.join(options.output, "PersistMain.cpp"), 'w')
    output.write(
        template.render_unicode(
            DAOOBJS=OBJECTS,
            PREFIX=options.prefix,
        ).encode('gb2312')
    )

    print " Done."

