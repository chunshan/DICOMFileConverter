#!/usr/bin/python
# -*- coding: UTF-8 -*- 

'''
this module parse the DICOM data converter config file
'''

__author__ = 'YANG Chunshan'

import xml.dom.minidom
from dicom_converter_logging import DICOMConvertLogger

def TagString2Tag(tag_string):
    """
    the string format looks like "0x00100010","0x00200020" 
    """
    num_string = tag_string[2:]
    return int(num_string, 16)

class DICOMDataConverterConfig(object):

    DICOM_VR = ["AE", "AS", "AT", "CS", 
        "DA", "DS", "DT", "FL", 
        "FD", "IS", "LO", "LT", 
        "OB", "OF", "OW", "PN",
        "SH", "SL", "SQ", "SS",
        "ST", "TM", "UI", "UL",
        "UN", "US", "UT"]

    NODE_ADD = "ADD"
    NODE_DELETE = "DELETE"
    NODE_MODIFY = "MODIFY"

    TAG_ID = "ID"
    TAG_VALUE = "Value"
    TAG_VR = "VR"
    TAG_REFERENCE_ID = "ReferenceTagID"
    TAG_REFERENCE_VR = "ReferenceTagVR"

    def __init__(self, config_path):
        self.config_path = config_path
        self.add_tags = []
        self.delete_tags = []
        self.modify_tags = []
        self.config_title = None
        self.customized_module_name = None
        self.customized_func_name = None
        self.logger = DICOMConvertLogger().getInstance()
		
    def Parse(self):
        """
        read ADD tags, DELETE tags, MODIFY tags from the config file
        """
        try:
            config_dom = xml.dom.minidom.parse(self.config_path)
            self.logger.info("%s is parsed by xml.dom successfully." % self.config_path)

            config_content = config_dom.documentElement

            add_content = config_content.getElementsByTagName("ADD")
            add_elements = add_content[0].getElementsByTagName("Tag")
            self.__ReadADDorModifyTags(add_elements, self.add_tags)
            self.logger.info("Read all ADD nodes successfully. There are %s tags to be added" % len(self.add_tags))

            delete_content = config_content.getElementsByTagName("DELETE")
            delete_elements = delete_content[0].getElementsByTagName("Tag")
            for element in delete_elements:
                tag_string = element.getAttribute("ID")
                tag = TagString2Tag(tag_string)
                self.delete_tags.append(tag)
            self.logger.info("Read all DELETE nodes successfully. There are  %s tags to be deleted." % len(self.delete_tags))

            modify_content = config_content.getElementsByTagName("MODIFY")
            modify_elements = modify_content[0].getElementsByTagName("Tag")
            self.__ReadADDorModifyTags(modify_elements, self.modify_tags)
            self.logger.info("Read all MODIFY nodes successfully. There are %s tags to be modified" % len(self.modify_tags))

            self.config_title = config_content.getAttribute("Title")

            customized_content = config_content.getElementsByTagName("CUSTOMIZED")
            if len(customized_content) == 0:
                self.logger.info("There is no customized config in the file.")
            else:
                module_element = customized_content[0].getElementsByTagName("ModuleName")
                self.customized_module_name = module_element[0].firstChild.data
                func_element = customized_content[0].getElementsByTagName("FunctionName")
                self.customized_func_name = func_element[0].firstChild.data

            self.logger.info("Read customized nodes successfully. " )

            self.logger.info("Read all contentes successfully in %s." % self.config_path)
        except StandardError, e:
            self.logger.error("Errors happen when parsing config: %s" % e.message)

    def __ReadADDorModifyTags(self, dom_elements, add_or_modify_tags):
        """
        a private method to get all add or modify tags
        """
        for element in dom_elements:
            tag_string = element.getAttribute("ID")
            tag = TagString2Tag(tag_string)
            vr = element.getAttribute("VR")
            if vr not in DICOMDataConverterConfig.DICOM_VR:
                raise ValueError("%s is not a valid DICOM VR" % vr)

            if element.hasAttribute("Value"):
                value = element.getAttribute("Value")
                add_or_modify_tags.append({"ID":tag, "VR":vr, "Value":value})
            elif element.hasAttribute("ReferenceTagID"):
                ref_tag_string = element.getAttribute("ReferenceTagID")
                ref_tag = TagString2Tag(ref_tag_string)
                ref_tag_vr = element.getAttribute("ReferenceTagVR")
                if ref_tag_vr not in DICOMDataConverterConfig.DICOM_VR:
                    raise ValueError("ReferenceTagVR: %s is not a valid DICOM VR" % ref_tag_vr)
                add_or_modify_tags.append({"ID":tag, "VR":vr, "ReferenceTagID":ref_tag, "ReferenceTagVR":ref_tag_vr})


if __name__ == '__main__':
    config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/converter_config.xml")
    # config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/philip2uih_dti.xml")
    config_example.Parse()
    print config_example.delete_tags
    print config_example.add_tags
    print config_example.modify_tags

    print config_example.config_title
    print config_example.customized_module_name
    print config_example.customized_func_name

