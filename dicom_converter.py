#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module aims to implement a dicom converter following the config file.
It has two parts. One part is the common dicom converter which can be represented by xml;
the other part is customized which must be implemented by code which can be loaded dynamically 
by the program.

The example of configuration file:
<Converter Title = "DTIConverter">
      <ADD>
           <Tag ID="0x00651037" VR="FD" ReferenceTagID="0x00189089" ReferenceTagVR="SH" />  <!--根据另一个tag填写一个tag -->
           <Tag ID="0x0065102B" VR="LT" Value="DTI_Func" />   <!--为一个tag赋固定值 -->
      </ADD>
      <DELETE>
           <Tag ID="0x00321060"/>  <!--删除tag --> 
      </DELETE>
      <MODIFY>
           <Tag ID="0x00080070" VR="LO" Value="UIH"/>
      </MODIFY>
      <CUSTOMIZED>   <!-- 自定义的转换 -->
           <ModuleName>dti_converter</ModuleName>
           <FunctionName>DTIConverter</FunctionName>
      </CUSTOMIZED>
</Converter>

If a customized module is necessary, the module(.py file) should be placed in 
the same folder with the configuration file.

And the function in the module should follow the format as below:

the input parameter is an object of DICOM file, so pydicom should be installed 
and dicom module should be imported.

def DICOMConverter(dicom_file):

TODO:
1, 增加进度显示，当修改的文件较多时不至于没有任何提示信息；
2，增加图像显示和一个文件的所有tag信息显示；
3，增加UI使得编辑ADD，DELETE和MODIFY的tag信息更加方便，不用直接编辑xml文件；
4，重构代码使得风格更加pythonic
"""

__author__ = 'YANG Chunshan'

import dicom
import logging
import os

from dicom_converter_config import DICOMDataConverterConfig
from dicom_file_reader import DICOMFileReader
import dicom_converter_common
import dicom_converter_customized

def ComposeNewFilePaths(new_folder_path, old_file_paths):
    """
    use the old file names but put them in another folder
    """
    new_file_paths = []
    for old_path in old_file_paths:
        file_name = os.path.basename(old_path)
        new_file_path = os.path.join(new_folder_path, file_name)
        new_file_paths.append(new_file_path)

    return new_file_paths


if __name__ == '__main__':
    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    while True:
        print "Please input a dicom file path or a dicom directory:"
        dicom_path = raw_input()
        # dicom_path = "D:/Project/PythonCode/dicom_converter/test/DEF FOIE ART. - 107198"

        print "Please input the config file path of dicom converter:"
        config_path = raw_input()
        # config_path = "D:/Project/PythonCode/dicom_converter/test/converter_config.xml"

        print "Please input the destination directory to contain the modified dicom:"
        dest_dir = raw_input()
        # dest_dir = "D:/Project/PythonCode/dicom_converter/test/newDEF"

        try:
            converter_config = DICOMDataConverterConfig(config_path)
            converter_config.Parse()

            dicom_file_reader = DICOMFileReader(dicom_path)
            dicom_file_reader.ReadDICOMFiles()

            new_file_paths = ComposeNewFilePaths(dest_dir, dicom_file_reader.dicom_file_paths)

            print "The name of DICOM converter is %s" % converter_config.config_title

            converter_customized = dicom_converter_customized.ConverterCustomized(converter_config)
            customized_method = converter_customized.GetCustomizedMethod()

            for i in range(len(new_file_paths)):
                dicom_file = dicom_file_reader.dicom_files[i]
                new_path = new_file_paths[i]

                dicom_converter_common.AddDICOMTags(dicom_file, converter_config.add_tags)
                dicom_converter_common.DeleteTags(dicom_file, converter_config.delete_tags)
                dicom_converter_common.ModifyTags(dicom_file, converter_config.modify_tags)

                # customized converter
                customized_method(dicom_file)

                dicom_file.save_as(new_path)

            print "DICOM files have been converted successfully!"
        except Exception, e:
            print e.message

