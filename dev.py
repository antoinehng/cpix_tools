# -*- coding: utf8 -*-

from cpixlib.cpix import Cpix

# Parse CPIX Document and extract useful informations
test = Cpix("path/to/cpix/document.xml")

# Returns JSON formated string
print(test.export_json())

# Writes and returns JSON file path
print(test.export_json_as_file())

# Returns XML formated string (based on Ateme Titan File preset XML structure)
print(test.export_titanfile_xml_as_file())

# Writes and returns XML file path (based on Ateme Titan File preset XML structure)
print(test.export_titanfile_xml_as_file())

# Updates the Ateme Titan File .kpreset file with CPIX informations
print(test.update_titanfile_kpreset_file("path/to/preset/for/update.kpreset"))

