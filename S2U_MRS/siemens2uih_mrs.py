#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module implements the conversion of MRS data from Siemens to UIH.
This module implements the part which cannot be expressed in the config file. 
"""

__author__ = 'YANG Chunshan'


import sys
sys.path.append("..")

import dicom
import logging
import struct

import siemens_csa_parser


def MRSSiemens2UIH(dicom_file):
    """
    this function translates Siemens MRS data to UIH MRS data.
    MagneticFieldStrength, TransmitterFrequency, SpectralWidth, EchoTime,etc
    these tags are read from siemens private CSA header.

    Note: the csa header 0x00291110,0x7fe10010,0x7fe11010,0x00291110,0x00291120 
    are perhaps different for different data.
    """
    try:
        logging.info("enter customized func: MRSSiemens2UIH")

        csa_header = dicom_file[0x00291110].value
        tag_list = siemens_csa_parser.SiemensCSAHeaderParser(csa_header)

        # # Manufacturer
        # manufacturer = "UIH"
        # dicom_file.add_new(0x00080070, "LO", manufacturer)

        # # SOPClassUID
        # sop_class_uid = "1.2.840.10008.5.1.4.1.1.4.2"
        # dicom_file.add_new(0x00080016, "UI", sop_class_uid)

        # # ResonantNucleus
        # resonant_nucleus = None
        # for tag in tag_list:
        #     if tag["Name"] == "ResonantNucleus":
        #         resonant_nucleus = tag["Data"][0]
        #         print "ResonantNucleus: %s" % resonant_nucleus
        #         break
        # resonant_nucleus = str(resonant_nucleus)
        # dicom_file.add_new(0x00189100, "CS", resonant_nucleus)

        # MagneticFieldStrength
        magnetic_strength = ""
        for tag in tag_list:
            if tag["Name"] == "MagneticFieldStrength":
                magnetic_strength = tag["Data"][0]
                #print "MagneticFieldStrength: %s" % magnetic_strength
                break
        magnetic_strength = str(magnetic_strength)
        dicom_file.add_new(0x00180087, "DS", magnetic_strength)
        logging.debug("MagneticFieldStrength with value: %s is inserted into the data." % magnetic_strength)

        #TransmitterFrequency
        transmitter_frequency = ""
        for tag in tag_list:
            if tag["Name"] == "ImagingFrequency":
                transmitter_frequency = tag["Data"][0]
                #print "TransmitterFrequency: %s" % transmitter_frequency
                break
        #transmitter_frequency = float(transmitter_frequency) * 1000
        transmitter_frequency = float(transmitter_frequency)
        dicom_file.add_new(0x00189098, "FD", transmitter_frequency)
        logging.debug("TransmitterFrequency with value: %s is inserted into the data." % transmitter_frequency)

        #SpectralWidth
        spectral_width = ""
        for tag in tag_list:
            if tag["Name"] == "RealDwellTime":
                spectral_width = tag["Data"][0]
                #print "RealDwellTime: %s" % spectral_width
                break
        spectral_width = 1.0 / float(spectral_width) * 1000000000
        #spectral_width = float(spectral_width)
        dicom_file.add_new(0x00189052, "FD", spectral_width)
        logging.debug("SpectralWidth with value: %s is inserted into the data." % spectral_width)

        #EchoTime
        echo_time = ""
        for tag in tag_list:
            if tag["Name"] == "EchoTime":
                echo_time = tag["Data"][0]
                #print "EchoTime: %s" % echo_time
                break
        echo_time = str(echo_time)
        dicom_file.add_new(0x00180081, "DS", echo_time)
        logging.debug("EchoTime with value: %s is inserted into the data." % echo_time)

        # RepetitionTime
        repetition_time = None
        for tag in tag_list:
            if tag["Name"] == "RepetitionTime":
                repetition_time = tag["Data"][0]
                #print "RepetitionTime: %s" % repetition_time
                break
        repetition_time = str(repetition_time)
        dicom_file.add_new(0x00180080, "DS", repetition_time)
        logging.debug("RepetitionTime with value: %s is inserted into the data." % repetition_time)

        # Columns
        columns = ""
        for tag in tag_list:
            if tag["Name"] == "Columns":
                columns = tag["Data"][0]
                #print "Columns: %s" % columns
                break
        columns = int(columns)
        dicom_file.add_new(0x00280011, "US", columns)
        logging.debug("Columns with value: %s is inserted into the data." % columns)

        # Rows
        rows = None
        for tag in tag_list:
            if tag["Name"] == "Rows":
                rows = tag["Data"][0]
                #print "Rows: %s" % rows
                break
        rows = int(rows)
        dicom_file.add_new(0x00280010, "US", rows)
        logging.debug("Rows with value: %s is inserted into the data." % rows)

        # NumberOfFrames
        number_of_frames = None
        for tag in tag_list:
            if tag["Name"] == "NumberOfFrames":
                number_of_frames = tag["Data"][0]
                #print "NumberOfFrames: %s" % number_of_frames
                break
        number_of_frames = str(number_of_frames)
        dicom_file.add_new(0x00280008, "IS", number_of_frames)
        logging.debug("NumberOfFrames with value: %s is inserted into the data." % number_of_frames)

        # DataPointColumns
        data_point_columns = None
        for tag in tag_list:
            if tag["Name"] == "DataPointColumns":
                data_point_columns = tag["Data"][0]
                #print "DataPointColumns: %s" % data_point_columns
                break
        data_point_columns = int(data_point_columns)
        dicom_file.add_new(0x00289002, "UL", data_point_columns)
        logging.debug("DataPointColumns with value: %s is inserted into the data." % data_point_columns)

        # FOVPosition
        fov_position = None
        for tag in tag_list:
            if tag["Name"] == "ImagePositionPatient":
                fov_position = tag["Data"][0:3]
                #print "FOVPosition: %s" % fov_position
                break
        dicom_file.add_new(0x0065ff01, "DS", fov_position)
        logging.debug("FOVPosition with value: %s is inserted into the data." % fov_position)

        #PixelSpacing
        pixel_spacing = None
        for tag in tag_list:
            if tag["Name"] == "PixelSpacing":
                pixel_spacing = tag["Data"][0:2]
                #print "PixelSpacing: %s" % pixel_spacing
                break

        #VoiThickness
        voi_thickness = None
        for tag in tag_list:
            if tag["Name"] == "VoiThickness":
                voi_thickness = tag["Data"][0]
                #print "VoiThickness: %s" % voi_thickness
                break

        #FOVPatient
        fov_patient = [float(pixel_spacing[0])*int(columns), float(pixel_spacing[1])*int(rows), float(voi_thickness)]
        #print "FOVPatient: %s" % fov_patient
        dicom_file.add_new(0x0065ff04, "DS", fov_patient)
        logging.debug("FOVPatient with value: %s is inserted into the data." % fov_patient)

        #VoiPhaseFov
        voi_phase_fov = None
        for tag in tag_list:
            if tag["Name"] == "VoiPhaseFoV":
                voi_phase_fov = tag["Data"][0]
                #print "VoiPhaseFoV: %s" % voi_phase_fov
                break

        #VoiReadoutFov
        voi_readout_fov = None
        for tag in tag_list:
            if tag["Name"] == "VoiReadoutFoV":
                voi_readout_fov = tag["Data"][0]
                #print "VoiReadoutFoV: %s" % voi_readout_fov
                break

        #VOIPatient
        voi_patient = [float(voi_phase_fov), float(voi_readout_fov), float(voi_thickness)]
        #print "VOIPatient: %s" % voi_patient
        dicom_file.add_new(0x0065ff05, "DS", voi_patient)
        logging.debug("VOIPatient with value: %s is inserted into the data." % voi_patient)

        # ImageOrientation
        image_orientation = None
        for tag in tag_list:
            if tag["Name"] == "ImageOrientationPatient":
                image_orientation = tag["Data"][0:6]
                #print "ImageOrientation: %s" % image_orientation
                break

        image_orientation = [float(s) for s in image_orientation]
        orientation_temp = image_orientation
        orientation_norm = [orientation_temp[1]*orientation_temp[5] - orientation_temp[2]*orientation_temp[4],
                            orientation_temp[2]*orientation_temp[3] - orientation_temp[0]*orientation_temp[5],
                            orientation_temp[0]*orientation_temp[4] - orientation_temp[1]*orientation_temp[3]]

        image_orientation[0:3] = [orientation * fov_patient[1] for orientation in image_orientation[0:3]]
        image_orientation[3:6] = [orientation * fov_patient[0] for orientation in image_orientation[3:6]]
        orientation_norm = [orientation * fov_patient[2] for orientation in orientation_norm]
        image_orientation.extend(orientation_norm)

        #print image_orientation
        dicom_file.add_new(0x0065ff02, "DS", image_orientation)
        logging.debug("ImageOrientation with value: %s is inserted into the data." % image_orientation)

        # spectroscopy data
        spectroscopy_data = dicom_file[0x7fe11010].value
        data_len = len(spectroscopy_data)
        str_format = str(data_len/4) + "f"
        item_val = struct.unpack(str_format, spectroscopy_data)
        item_val = [item for item in item_val]
        #print data_len / 4
        #print len(item_val)
        dicom_file.add_new(0x56000020, "OF", item_val) 
        logging.debug("Spectroscopy data is inserted into the data. Point number: %s" % len(item_val))

        #print dicom_file[0x56000020].VM 

        del dicom_file[0x7fe10010]
        del dicom_file[0x7fe11010]
        del dicom_file[0x00291110] 
        del dicom_file[0x00291120]
        logging.debug("Delete Siemens Image CSA header, Series CSA header, and Spectroscopy data successfully.")  

        logging.info("Exit customized func: MRSSiemens2UIH successfully.")
    except Exception, e:
        logging.error("errors happen in MRSSiemens2UIH. Error is: %s" % e.message)


if __name__ == '__main__':
    import os

    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    s_csi_info = dicom.read_file("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_CSI.IMA")
    MRSSiemens2UIH(s_csi_info)
    s_csi_info.save_as("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_CSI_UIH_del_S_Data.IMA")

    del s_csi_info[0x56000020]
    s_csi_info.save_as("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_CSI_UIH_del_no_data.IMA")

    s_svs_info = dicom.read_file("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_SVS.IMA")
    MRSSiemens2UIH(s_svs_info)
    s_svs_info.save_as("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_SVS_UIH_del_S_Data.IMA")

    del s_svs_info[0x56000020]
    s_svs_info.save_as("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_SVS_UIH_del_no_data.IMA")
