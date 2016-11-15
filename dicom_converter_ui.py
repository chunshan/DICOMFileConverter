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
import os,glob,time
import threading
import exceptions

from dicom_converter_config import DICOMDataConverterConfig
from dicom_file_reader import DICOMFileReader
import dicom_converter_common
import dicom_converter_customized

from dicom_converter_logging import DICOMConvertLogger
           


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

class SeriesDicomConverter(threading.Thread):
    '''provide a dicom converter class for series'''
    def __init__(self,series_convert_paras,series_id_list,threadName='Series DICOM Converter'):
        threading.Thread.__init__(self,name=threadName)
        self.series_convert_paras = series_convert_paras        
        self.series_id_list = series_id_list
        self.total_number_series = len(self.series_id_list)
        self.converted_files_curr_series = 0
        self.total_number_files_curr_series = 0       
        self.series_convert_finished_curr = False
        self.series_convert_finished_all = False
        self.index = 0
        self.continued = False
        self.logger = DICOMConvertLogger().getInstance()
        
    
    def setTagToContinue(self):
        self.continued = True
            
    def getTotalFilesInCurrSeries(self):
        '''return the total number of files at current series'''
        filePath = self.series_convert_paras[self.index][0]
        lsFiles = glob.glob(filePath + os.sep + "*.dcm")
        self.total_number_files_curr_series = len(lsFiles)
        return self.total_number_files_curr_series
    
    def getFinishedFilesInCurrSeries(self):
        return self.converted_files_curr_series
    
    def getFinishedSeiresNumber(self):
        return self.index
    
    def isCurrSeriesConvertFinished(self):
        return self.series_convert_finished_curr
    
    def isAllSeriesConvertFinished(self):
        return self.series_convert_finished_all
            
    def run(self):
        '''convert the series'''
        try:
            while not self.series_convert_finished_all:
                config_file_name = self.series_convert_paras[self.index][2] 
                converter_config = DICOMDataConverterConfig(config_file_name)
                converter_config.Parse()
    
                src_file_path = self.series_convert_paras[self.index][0]
                dicom_file_reader = DICOMFileReader(src_file_path)
                dicom_file_reader.ReadDICOMFiles()
                
                dst_file_path = self.series_convert_paras[self.index][1]                
                dest_dir = dst_file_path + os.sep + self.series_id_list[self.index]
                if not os.path.exists(dest_dir):
                    os.mkdir(dest_dir)     
                new_file_paths = ComposeNewFilePaths(dest_dir,dicom_file_reader.dicom_file_paths)
    
                self.logger.info("The name of DICOM converter is %s" % converter_config.config_title)
    
                converter_customized = dicom_converter_customized.ConverterCustomized(converter_config)
                customized_method = converter_customized.GetCustomizedMethod()
                try:
                    for i in range(len(new_file_paths)):
                        dicom_file = dicom_file_reader.dicom_files[i]
                        new_path = new_file_paths[i]
        
                        dicom_converter_common.AddDICOMTags(dicom_file, converter_config.add_tags)
                        dicom_converter_common.DeleteTags(dicom_file, converter_config.delete_tags)
                        dicom_converter_common.ModifyTags(dicom_file, converter_config.modify_tags)
        
                        # customized converter
                        if customized_method is not None:
                            customized_method(dicom_file)
        
                        dicom_file.save_as(new_path)
                        self.converted_files_curr_series += 1
                        if self.converted_files_curr_series == self.total_number_files_curr_series:
                            self.series_convert_finished_curr = True 
                    self.logger.info("DICOM files of series instance id = %s have been converted successfully!" %self.series_id_list[self.index])
                except Exception,e:
                    self.logger.error("DICOM files of series instance id = %s failed to be converted!" %self.series_id_list[self.index])
                    self.series_convert_finished_curr = True  # skip the series convert        
                    
                self.index += 1
                if self.index == self.total_number_series:
                    # all series are converted
                    self.series_convert_finished_all = True
                else:
                    # wait gui updated then continue
                    while not self.continued:
                        time.sleep(1)
                    # reset the tags for next series
                    self.converted_files_curr_series = 0
                    self.series_convert_finished_curr = False
                    self.continued = False
                
        except Exception, e:
                self.logger.error(e.message)
   


if __name__ == '__main__':
    series_convert_paras = [(r'E:\Images\20160627\1.2.156.112605.161344306039.20160627012728.2.8764.1\1.2.156.112605.161344306039.20160627012823.3.7748.1',r'E:\packages',r'E:\packages\20161114\1.2.156.112605.161344306039.20160627012823.3.7748.1.xml')]
    series_id_list = ['1.2.156.112605.161344306039.20160627012728.2.8764.1']
    converter = SeriesDicomConverter(series_convert_paras,series_id_list)
    converter.run()

