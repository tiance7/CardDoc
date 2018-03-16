# -*- coding: cp936 -*-

import os
import glob
import data_converter

converter = data_converter.DataConverter()
fileList = glob.glob(os.path.join(".\\template", "*.xml"))
for aFilePath in fileList:
    converter.Eat(aFilePath)
    
converter.MakeXml(os.path.join(".\\template", data_converter.EXCEL_XML_DIR_NAME))
