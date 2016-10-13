#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module aims to implement common dicom converter following the config file
"""

__author__ = 'YANG Chunshan'

import dicom
import logging

from dicom_converter_config import DICOMDataConverterConfig



DICOM_STRING_VR = ["AS", "CS", "DA", "DS",
                   "DT", "IS", "LO", "LT", 
                   "PN", "SH", "ST", "TM", 
                   "UI", "UN", "UT"]

DICOM_INT_VR = ["US", "UL", "SS", "SL"]

DICOM_FLOAT_VR = ["FL", "FD"]

DICOM_BYTE_VR = ["OB", "OW"]   

def AddDICOMTags(dicom_file, add_tags):
    """
    add dicom tags into one dicom file.
    limit: 1, SQ,OB,OW,AE are not supported
           2, validity of the value (VR) is not checked strictly
    """
    for tag in add_tags:
        if tag["ID"] in dicom_file:
            logging.info("tag %#x is already in dicom file." % tag["ID"])
            continue

        add_value = None
        if tag.has_key("Value"):
            add_value = tag["Value"].split("\\")
        elif tag.has_key("ReferenceTagID"):
            if tag["ReferenceTagID"] in dicom_file:
                add_value = dicom_file[tag["ReferenceTagID"]].value
            else:
                logging.warning("reference tag %#x doesn't exist." % tag["ReferenceTagID"])
        else:
            logging.warning("the need-to-add tag %#x lacks of content." % tag["ID"])
            continue

        try:
            if tag["VR"] in DICOM_STRING_VR:
                dicom_file.add_new(tag["ID"], tag["VR"], add_value)
            elif tag["VR"] in DICOM_INT_VR:
                if isinstance(add_value, list):
                    add_value_int = map(int, add_value)
                    dicom_file.add_new(tag["ID"], tag["VR"], add_value_int)
                else:
                    int_value = int(add_value)
                    dicom_file.add_new(tag["ID"], tag["VR"], int_value)
            elif tag["VR"] in DICOM_FLOAT_VR:
                if isinstance(add_value, list):
                    add_value_float = map(float, add_value)
                    dicom_file.add_new(tag["ID"], tag["VR"], add_value_float)
                else:
                    float_value = float(add_value)
                    dicom_file.add_new(tag["ID"], tag["VR"], float_value)
            else:
                logging.warning("%s is not a supported VR yet" % tag["VR"])
        except Exception, e:
            logging.error("Fail to add new tag %#x into dicom file: %s" % (tag["ID"], e.message)) 

    logging.debug("Add related tags finished.")

"""delete tags from one dicom file"""
def DeleteTags(dicom_file, delete_tags):
    for tag in delete_tags:
        if tag in dicom_file:
            del dicom_file[tag]
        else:
            logging.info("Tag %#x doesn't exist in the dicom file." % tag)

    logging.debug("Delete related tags finished.")

"""modify tags in one dicom file"""
def ModifyTags(dicom_file, modify_tags):
    """
    modify dicom tags in the dicom file.
    limit: 1, SQ,OB,OW,AE are not supported
           2, validity of the value (VR) is not checked strictly
    """
    for tag in modify_tags:
        if tag["ID"] not in dicom_file:
            logging.warning("tag %#x is not in dicom file." % tag["ID"])
            continue

        modify_value = None
        if tag.has_key("Value"):
            modify_value = tag["Value"].split("\\")
        elif tag.has_key("ReferenceTagID"):
            if tag["ReferenceTagID"] in dicom_file:
                modify_value = dicom_file[tag["ReferenceTagID"]].value
            else:
                logging.warning("reference tag %#x doesn't exist." % tag["ReferenceTagID"])
        else:
            logging.warning("the need-to-modify tag %#x lacks of content." % tag["ID"])
            continue

        try:
            if tag["VR"] in DICOM_STRING_VR:
                dicom_file[tag["ID"]].value = modify_value
            elif tag["VR"] in DICOM_INT_VR:
                if isinstance(modify_value, list):
                    modify_value_int = map(int, modify_value)
                    dicom_file[tag["ID"]].value = modify_value_int
                else:
                    int_value = int(modify_value)
                    dicom_file[tag["ID"]].value = int_value
            elif tag["VR"] in DICOM_FLOAT_VR:
                if isinstance(modify_value, list):
                    modify_value_float = map(float, modify_value)
                    dicom_file[tag["ID"]].value = modify_value_float
                else:
                    float_value = float(modify_value)
                    dicom_file[tag["ID"]].value = float_value
            else:
                logging.warning("%s is not a supported VR yet" % tag["VR"])
        except Exception, e:
            logging.error("Fail to modify value of tag %#x in the dicom file: %s" % (tag["ID"], e.message)) 

    logging.debug("Modify related tags finished.")  

if __name__ == '__main__':

    import os
    from dicom_file_reader import DICOMFileReader


    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    #config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/converter_config.xml")
    config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/philip2uih_dti.xml")
    config_example.Parse()

    dicom_file_reader = DICOMFileReader("D:/Philips/YL_DTI/00033.dcm")
    dicom_file_reader.ReadDICOMFiles()

    for dicom_file in dicom_file_reader.dicom_files:
        AddDICOMTags(dicom_file, config_example.add_tags)
        DeleteTags(dicom_file, config_example.delete_tags)
        ModifyTags(dicom_file, config_example.modify_tags)

        dicom_file.save_as("D:/modified.dcm")


