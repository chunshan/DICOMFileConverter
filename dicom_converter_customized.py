#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
this module aims to load customized dicom converter module implemented by other people
'''

__author__ = 'YANG Chunshan'

import os
import sys
import importlib
import logging

import dicom_converter_config


class ConverterCustomized(object):
    """get customized converter method"""
    def __init__(self, converter_config):
        self.converter_config = converter_config

    def GetCustomizedMethod(self):
        if self.converter_config is None or self.converter_config.customized_module_name is None:
            logging.warning("there is no customized converter.")
            return None

        config_dir = os.path.split(self.converter_config.config_path)[0]
        if config_dir not in sys.path:
            sys.path.append(config_dir)

        try:
            module_name = self.converter_config.customized_module_name
            func_name = self.converter_config.customized_func_name
            customized_moudle = importlib.import_module(module_name)
            customized_func = getattr(customized_moudle, func_name)
            logging.info("load customized module and function successfully. \
                module name:%s, function name:%s" % (module_name, func_name))
            return customized_func
        except Exception, e:
            logging.error("Fail to import the customized module and function name.%s" % e.message)
        




if __name__ == '__main__':
    import os
    from dicom_file_reader import DICOMFileReader
    from dicom_converter_config import DICOMDataConverterConfig


    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    #config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/converter_config.xml")
    config_example = DICOMDataConverterConfig("D:/Project/PythonCode/dicom_converter/test/P2U/philip2uih_dti.xml")
    config_example.Parse()

    p2u_customized = ConverterCustomized(config_example)
    p2u_dti = p2u_customized.GetCustomizedMethod()
    p2u_dti("This is a customized p2u dti file.")
