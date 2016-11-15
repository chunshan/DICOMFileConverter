#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module converts UIH MRS DICOM format to RDA format.  
"""

__author__ = 'chunshan.yang@united-imaging.com'


import sys
sys.path.append("..")

import dicom
import logging

import uih2rda_mrs
from dicom_file_reader import DICOMFileReader

def ComposeNewFilePaths(new_folder_path, old_file_paths, file_extension):
    """
    use the old file names but put them in another folder
    """
    new_file_paths = []
    for old_path in old_file_paths:
        file_name = os.path.basename(old_path)
        file_name_no_extension = os.path.splitext(file_name)[0]
        new_file_name = "".join((file_name_no_extension, ".", file_extension))
        new_file_path = os.path.join(new_folder_path, new_file_name)
        new_file_paths.append(new_file_path)

    return new_file_paths

def ReplaceFilesExtension(old_file_paths, file_extension):
    """
    change files' extension with full path
    """
    new_file_paths = []
    for old_path in old_file_paths:
        file_name = os.path.basename(old_path)
        file_name_no_extension = os.path.splitext(file_name)[0]
        new_file_name = "".join((file_name_no_extension, ".", file_extension))

        old_file_dir = os.path.split(old_path)[0]
        new_file_path = os.path.join(old_file_dir, new_file_name)
        new_file_paths.append(new_file_path)

    return new_file_paths


if __name__ == '__main__':
    import os

    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    while True:
        print "Please input a dicom file path or a dicom directory which contains UIH MRS file(s):"
        dicom_path = raw_input()
        # dicom_path = "D:/Project/PythonCode/dicom_converter/test/DEF FOIE ART. - 107198"

        print "\n\n"

        # print "Please input the destination directory to contain the converted rda files:"
        # dest_dir = raw_input()
        # # dest_dir = "D:/Project/PythonCode/dicom_converter/test/newDEF"
        # print "\n"

        try:
            dicom_file_reader = DICOMFileReader(dicom_path)
            dicom_file_reader.ReadDICOMFiles()

            new_file_paths = ReplaceFilesExtension(dicom_file_reader.dicom_file_paths, "rda")

            for i in range(len(new_file_paths)):
                dicom_file = dicom_file_reader.dicom_files[i]
                new_path = new_file_paths[i]

                rda_file = uih2rda_mrs.RDAFile(new_path)
                uih2rda_mrs.MRSUIH2RDA(dicom_file, rda_file)
                rda_file.WriteFile()

            print "UIH MRS DICOM files have been converted to RDA files successfully!"
            print "Converted RDA files are placed under the same folder with the dicom files!"
            print "\n\n"
        except Exception, e:
            print e.message
            print "\n\n"

