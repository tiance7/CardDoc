#!/usr/bin/python

import sys, os, os.path

# import bundled MakoTemplates module
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), 'MakoTemplates.zip'))

import xml.dom.minidom

from mako.runtime import Context
from mako.template import Template

tools_dir = os.path.dirname(os.path.realpath(__file__))

def generate_ids(input_path, output_path):

    print input_path, output_path

    dom = xml.dom.minidom.parse(input_path)
    root = dom.documentElement
    oids = root.getElementsByTagName('object')

    OBJECT_IDS = []
    for oid in oids:
        if oid.getAttribute('tag') not in set(["DAO_TYPE_OBJECT", "DAO_TYPE_PROXY", "DAO_TYPE_QUERY", "DAO_TYPE_PROC", "DAO_TYPE_MAX"]):
            if not oid.getAttribute('tag').startswith("DAO_TYPE_TEST_"):
                OBJECT_IDS.append([oid.getAttribute('tag'), oid.firstChild.data, oid.getAttribute('comment')])

    template = Template(filename=os.path.join(tools_dir, "templates/ids_h.mako"))
    output = file(output_path, 'w')
    output.write(
        template.render_unicode(
            OBJECT_IDS=OBJECT_IDS
        ).encode('gb2312')
    )


if __name__ == "__main__":
    """
    usage: ids2go.py INL_FILE OUT_FILE
    """
    input_path = sys.argv[1]
    output_path = "ids.go"
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    generate_ids(input_path, output_path)


