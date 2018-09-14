# -*- coding: utf8 -*-

from cpixlib.cpix import Cpix

test = Cpix("/Users/antoine/Desktop/cpix.xml")
print(test)

print(test.export_json_as_file())

print(test.export_titanfile_xml_as_file())
