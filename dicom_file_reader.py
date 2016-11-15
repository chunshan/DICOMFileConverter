#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import dicom
import os,glob
from dicom_converter_logging import DICOMConvertLogger

"""
this module parse the DICOM data for a given path/file.
"""

__author__ = 'YANG Chunshan'

def Logger():
    return DICOMConvertLogger().getInstance()

def IsSubString(sub_str_list, str):  
    ''''' 
    #判断字符串str是否包含序列sub_str_list中的每一个子字符串 
    #>>>sub_str_list = ['F','EMS','txt'] 
    #>>>Str='F06925EMS91.txt' 
    #>>>IsSubString(sub_str_list, Str)  #return True (or False) 
    '''
    flag = True  
    for substr in sub_str_list:  
        if not (substr in str):  
            flag = False  
  
    return flag

def GetFileList2(find_path, suffix = []):
    """获取目录中指定后缀名的文件列表"""
    try:
        file_lists = []
        if len(suffix) == 0:
            file_lists = glob.glob(find_path + os.sep + "*")
            return file_lists

        for each_suffix in suffix:
            each_file_lists = glob.glob(find_path + os.sep + each_suffix)
            file_lists.extend(each_file_lists)

        return file_lists
    except Exception, e:
        Logger().error("errors happen in GetFileList2")

def GetFileListRecursively(find_path, flag_str = []): 
    """ 
    #递归地获取目录中及其子目录中指定的文件名 
     #>>>flag_str=['F','EMS','txt'] #要求文件名称中包含这些字符 
     #>>>file_list = Getfile_list(find_path, flag_str) # 
    """
    try:
        file_list = []
        if os.path.isfile(find_path):
            #Logger().debug("%s is a file." % find_path)
            path_filename = os.path.split(find_path)
            if len(flag_str) > 0:
                if IsSubString(flag_str, path_filename[1]):
                    file_list.append(find_path)
                    return file_list
                else:
                    return []
            else:
                file_list.append(find_path)
                return file_list

        #Logger().debug("%s is a dir." % find_path)
        if not find_path.endswith("/"):
            find_path = find_path + "/"

        dir_or_files = os.listdir(find_path)
        if len(dir_or_files) > 0:
            for dir_file in dir_or_files:
                full_path = os.path.join(find_path, dir_file)
                temp_file_list = GetFileListRecursively(full_path, flag_str)
                for file_path in temp_file_list:
                    file_list.append(file_path)
                
            return file_list
        else:
            return []

    except Exception, e:
        #Logger().error("errors happen in GetFileListRecursively")
        print e.message

def GetFileList(find_path, flag_str = []): 
    """ 
    #获取目录中指定的文件名 
     #>>>flag_str=['F','EMS','txt'] #要求文件名称中包含这些字符 
     #>>>file_list = Getfile_list(find_path, flag_str) # 
    """
    try:
        file_list = []
        if os.path.isfile(find_path):
            Logger().debug("%s is a file." % find_path)
            file_list.append(find_path)
            return file_list

        Logger().debug("%s is a dir." % find_path)
        file_names = os.listdir(find_path)
        if (len(file_names) > 0):
            for fn in file_names:
                if (len(flag_str) > 0):
                    if (IsSubString(flag_str, fn)):
                        full_file_name = os.path.join(find_path,fn) 
                        file_list.append(full_file_name)
                else:
                #默认直接返回所有文件名
                    full_file_name = os.path.join(find_path, fn) 
                    file_list.append(full_file_name) 
        #对文件名排序 
        if (len(file_list) > 0): 
            file_list.sort()

        Logger().info("There are %s files under %s." % (len(file_names), find_path))

        return file_list
    except Exception, e:
        Logger().error("errors happen in GetFileList")

class DICOMFileReader(object):
    """
    read all dicom files for the given dir/file path. 
    """
    def __init__(self, dicom_path):
        self.dicom_path = dicom_path
        self.dicom_files = []
        self.dicom_file_paths = []

    def ReadDICOMFiles(self):
        """
        dicom_path is a file or a dir. If it is a dir, parse all files under the dir
        """
        try:
            fail_to_parse = []

            self.dicom_file_paths = GetFileListRecursively(self.dicom_path)
            for path in self.dicom_file_paths:
                try:
                    dicom_file = dicom.read_file(path)
                    self.dicom_files.append(dicom_file)
                except Exception, e:
                    fail_to_parse.append(path)
                    Logger().error("fail to pare dicom file %s" % path)

            Logger().info("%s dicom file are parsed successfully" % len(self.dicom_files))

            if len(self.dicom_file_paths) != len(self.dicom_files):
                for fail_path in fail_to_parse:
                    self.dicom_file_paths.remove(fail_path)
                Logger().info("remove the fail-to-parse path. the count of failed files is:%s" % len(fail_to_parse))

        except Exception, e:
            Logger().error("errors happen when read dicom files")

if __name__ == '__main__':
    file_lists = GetFileListRecursively("D:/Philips/YL_DTI", [".dcm"])
    print  file_lists
    # one_file_reader = DICOMFileReader("D:/Project/PythonCode/dicom_converter/test/DEF FOIE ART. - 107198/IM-0001-0002.dcm")
    # one_file_reader.ReadDICOMFiles()
    # print one_file_reader.dicom_file_paths

    # multi_file_reader = DICOMFileReader("D:/Project/PythonCode/dicom_converter/test/DEF FOIE ART. - 107198")
    # multi_file_reader.ReadDICOMFiles()
    # print multi_file_reader.dicom_file_paths

