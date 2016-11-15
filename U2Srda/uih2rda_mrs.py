#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module converts UIH MRS DICOM format to RDA format.  
"""

__author__ = 'chunshan.yang@united-imaging.com'

import dicom
import logging
import struct

def GetTagValue(dicom_file, tag):
    """
    get value safely from the dicom file.
    """
    try:
        if dicom_file.has_key(tag):
            return dicom_file[tag].value
        else:
            logging.warning("Tag: %x does not exist in the dicom file." % tag)
            return None
    except Exception, e:
        logging.error("Errors happen when getting value from DICOM. Tag: %x. Error is: %s. " % (tag, e))
        return None


def MRSUIH2RDA(dicom_file, rda_file):
    """
    this function translates UIH MRS data (DICOM format) to RDA data format.

    RDA format:
    >>> Begin of header <<<
    PatientName: SPECTR TEST1
    PatientID: 209120611
    PatientSex: M
    *****
    >>> End of header <<<
    Raw MR Spectroscopy data stream
    """
    try:
        logging.info("enter main func MRSUIH2RDA")

        #PatientName
        patient_name = GetTagValue(dicom_file, 0x00100010)
        rda_file.AddKeyValue("PatientName", patient_name)

        #PatientID
        patient_id = GetTagValue(dicom_file, 0x00100020)
        rda_file.AddKeyValue("PatientID", patient_id)

        #PatientSex
        patient_sex = GetTagValue(dicom_file, 0x00100040)
        rda_file.AddKeyValue("PatientSex", patient_sex)

        #PatientBirthDate
        patient_birthdate = GetTagValue(dicom_file, 0x00100030)
        rda_file.AddKeyValue("PatientBirthDate", patient_birthdate)

        #StudyDate
        study_date = GetTagValue(dicom_file, 0x00080020)
        rda_file.AddKeyValue("StudyDate", study_date)

        #StudyTime
        study_time = GetTagValue(dicom_file, 0x00080030)
        rda_file.AddKeyValue("StudyTime", study_time)

        #StudyDescription
        study_description = GetTagValue(dicom_file, 0x00081030)
        rda_file.AddKeyValue("StudyDescription", study_description)

        #PatientAge
        patient_age = GetTagValue(dicom_file, 0x00101010)
        rda_file.AddKeyValue("PatientAge", patient_age)

        #PatientWeight
        patient_weight = GetTagValue(dicom_file, 0x00101030)
        rda_file.AddKeyValue("PatientWeight", patient_weight)

        #SeriesDate
        series_date = GetTagValue(dicom_file, 0x00080021)
        rda_file.AddKeyValue("SeriesDate", series_date)

        #SeriesTime
        series_time = GetTagValue(dicom_file, 0x00080031)
        rda_file.AddKeyValue("SeriesTime", series_time)

        #SeriesDescription
        series_description = GetTagValue(dicom_file, 0x0008103e)
        rda_file.AddKeyValue("SeriesDescription", series_description)

        #ProtocolName
        protocol_name = GetTagValue(dicom_file, 0x00181030)
        rda_file.AddKeyValue("ProtocolName", protocol_name)

        #PatientPosition
        patient_position = GetTagValue(dicom_file, 0x00185100)
        rda_file.AddKeyValue("PatientPosition", patient_position)

        #SeriesNumber
        series_number = GetTagValue(dicom_file, 0x00200011)
        rda_file.AddKeyValue("SeriesNumber", series_number)

        #InstitutionName
        institution_name = GetTagValue(dicom_file, 0x00080080)
        rda_file.AddKeyValue("InstitutionName", institution_name)

        #StationName
        station_name = GetTagValue(dicom_file, 0x00081010)
        rda_file.AddKeyValue("StationName", station_name)

        #ModelName
        model_name = GetTagValue(dicom_file, 0x00081090)
        rda_file.AddKeyValue("ModelName", model_name)

        #DeviceSerialNumber
        device_serial_number = GetTagValue(dicom_file, 0x00181000)
        rda_file.AddKeyValue("DeviceSerialNumber", device_serial_number)

        #SoftwareVersion
        software_version = GetTagValue(dicom_file, 0x00181020)
        rda_file.AddKeyValue("SoftwareVersion", software_version)

        #InstanceDate
        instance_date = GetTagValue(dicom_file, 0x00080012)
        rda_file.AddKeyValue("InstanceDate", instance_date)

        #InstanceTime
        instance_time = GetTagValue(dicom_file, 0x00080013)
        rda_file.AddKeyValue("InstanceTime", instance_time)

        #InstanceNumber 
        instance_number = GetTagValue(dicom_file, 0x00200013)
        rda_file.AddKeyValue("InstanceNumber", instance_number)

        #InstanceComments
        instance_comments = GetTagValue(dicom_file, 0x00204000)
        rda_file.AddKeyValue("InstanceComments", instance_comments)

        #AcquisitionNumber
        acquisition_number = GetTagValue(dicom_file, 0x00200012)
        rda_file.AddKeyValue("AcquisitionNumber", acquisition_number)

        #SequenceName
        sequence_name = GetTagValue(dicom_file, 0x00180024)
        rda_file.AddKeyValue("SequenceName", sequence_name)

        #SequenceDescription, same to SequenceName
        sequence_description = GetTagValue(dicom_file, 0x00180024)
        rda_file.AddKeyValue("SequenceDescription", sequence_description)

        #TR
        tr = GetTagValue(dicom_file, 0x00180080)
        rda_file.AddKeyValue("TR", tr)

        #TE
        te = GetTagValue(dicom_file, 0x00180081)
        rda_file.AddKeyValue("TE", te)

        #TM, not found
        tm = GetTagValue(dicom_file, 0x00294000)
        rda_file.AddKeyValue("TM", tm)

        #TI
        ti = GetTagValue(dicom_file, 0x00180082)
        rda_file.AddKeyValue("TI", ti)

        #DwellTime, 1E6/Spectral Width,（0018,9052） ?
        spectral_width = float(GetTagValue(dicom_file, 0x00189052))
        dwell_time = 1000000.0 / spectral_width
        rda_file.AddKeyValue("DwellTime", dwell_time)

        #EchoNumber
        echo_number = GetTagValue(dicom_file, 0x00180086)
        rda_file.AddKeyValue("EchoNumber", echo_number)

        #NumberOfAverages
        number_of_averages = GetTagValue(dicom_file, 0x00180083)
        rda_file.AddKeyValue("NumberOfAverages", number_of_averages)

        #MRFrequency
        mr_frequency = GetTagValue(dicom_file, 0x00189098)
        rda_file.AddKeyValue("MRFrequency", mr_frequency)

        #Nucleus
        nucleus = GetTagValue(dicom_file, 0x00189100)
        rda_file.AddKeyValue("Nucleus", nucleus)

        #MagneticFieldStrength
        magnetic_field_strength = GetTagValue(dicom_file, 0x00180087)
        rda_file.AddKeyValue("MagneticFieldStrength", magnetic_field_strength)

        #NumOfPhaseEncodingSteps
        number_of_phase_encoding_steps = GetTagValue(dicom_file, 0x00180089)
        rda_file.AddKeyValue("NumOfPhaseEncodingSteps", number_of_phase_encoding_steps)

        #FlipAngle
        flip_angle = GetTagValue(dicom_file, 0x00181314)
        rda_file.AddKeyValue("FlipAngle", flip_angle)

        #VectorSize
        vector_size = GetTagValue(dicom_file, 0x00189127)
        rda_file.AddKeyValue("VectorSize", vector_size)

        #CSIMatrixSize[0]
        csi_matrix_size0 = GetTagValue(dicom_file, 0x00189095)
        rda_file.AddKeyValue("CSIMatrixSize[0]", csi_matrix_size0)

        #CSIMatrixSize[1]
        csi_matrix_size1 = GetTagValue(dicom_file, 0x00189234)
        rda_file.AddKeyValue("CSIMatrixSize[1]", csi_matrix_size1)

        #CSIMatrixSize[2]
        csi_matrix_size2 = GetTagValue(dicom_file, 0x00189159)
        rda_file.AddKeyValue("CSIMatrixSize[2]", csi_matrix_size2)

        #CSIMatrixSizeOfScan[0]
        #csi_matrix_size_of_scan0 = GetTagValue(dicom_file, 0x00189127)
        csi_matrix_size_of_scan0 = 1
        rda_file.AddKeyValue("CSIMatrixSizeOfScan[0]", csi_matrix_size_of_scan0)

        #CSIMatrixSizeOfScan[1]
        #csi_matrix_size_of_scan1 = GetTagValue(dicom_file, 0x00189127)
        csi_matrix_size_of_scan1 = 1
        rda_file.AddKeyValue("CSIMatrixSizeOfScan[1]", csi_matrix_size_of_scan1)

        #CSIMatrixSizeOfScan[2]
        #csi_matrix_size_of_scan2 = GetTagValue(dicom_file, 0x00189127)
        csi_matrix_size_of_scan2 = 1
        rda_file.AddKeyValue("CSIMatrixSizeOfScan[2]", csi_matrix_size_of_scan2)

        #CSIGridShift[0]
        #csi_grid_shift0 = GetTagValue(dicom_file, 0x00189127)
        csi_grid_shift0 = 0
        rda_file.AddKeyValue("CSIGridShift[0]", csi_grid_shift0)

        #CSIGridShift[1]
        #csi_grid_shift1 = GetTagValue(dicom_file, 0x00189127)
        csi_grid_shift1 = 0
        rda_file.AddKeyValue("CSIGridShift[1]", csi_grid_shift1)

        #CSIGridShift[2]
        #csi_grid_shift2 = GetTagValue(dicom_file, 0x00189127)
        csi_grid_shift2 = 0
        rda_file.AddKeyValue("CSIGridShift[2]", csi_grid_shift2)

        #HammingFilter, right?
        hamming_filter = GetTagValue(dicom_file, 0x00200040)
        rda_file.AddKeyValue("HammingFilter", hamming_filter)

        #FrequencyCorrection
        frequency_correction = GetTagValue(dicom_file, 0x00189101)
        rda_file.AddKeyValue("FrequencyCorrection", frequency_correction)

        #TransmitCoil
        transmit_coil = GetTagValue(dicom_file, 0x00181251)
        rda_file.AddKeyValue("TransmitCoil", transmit_coil)

        #TransmitRefAmplitude[1H] , not found
        #transmit_ref_amplitude = GetTagValue(dicom_file, 0x00189127)
        transmit_ref_amplitude = 380
        rda_file.AddKeyValue("TransmitRefAmplitude[1H]", transmit_ref_amplitude)

        #SliceThickness
        slice_thickness = GetTagValue(dicom_file, 0x00180050)
        rda_file.AddKeyValue("SliceThickness", slice_thickness)

        image_position_patient = GetTagValue(dicom_file, 0x00200032)
        if (image_position_patient is not None) and (len(image_position_patient) >= 3):
            #PositionVector[0]
            position_vector0 = image_position_patient[0]
            rda_file.AddKeyValue("PositionVector[0]", position_vector0)

            #PositionVector[1]
            position_vector1 = image_position_patient[1]
            rda_file.AddKeyValue("PositionVector[1]", position_vector1)

            #PositionVector[2]
            position_vector2 = image_position_patient[2]
            rda_file.AddKeyValue("PositionVector[2]", position_vector2)
        else:
            logging.error("Cannot add PositionVector [0][1][2]")

        
        image_orientation_patient = GetTagValue(dicom_file, 0x00200037)
        if (image_orientation_patient is not None) and (len(image_orientation_patient) >= 6):
            #RowVector[0]
            row_vector0 = image_orientation_patient[0]
            rda_file.AddKeyValue("RowVector[0]", row_vector0)

            #RowVector[1]
            row_vector1 = image_orientation_patient[1]
            rda_file.AddKeyValue("RowVector[1]", row_vector1)

            #RowVector[2]
            row_vector2 = image_orientation_patient[2]
            rda_file.AddKeyValue("RowVector[2]", row_vector2)

            #ColumnVector[0]
            column_vector0 = image_orientation_patient[3]
            rda_file.AddKeyValue("ColumnVector[0]", column_vector0)

            #ColumnVector[1]
            column_vector1 = image_orientation_patient[4]
            rda_file.AddKeyValue("ColumnVector[1]", column_vector1)

            #ColumnVector[2]
            column_vector2 = image_orientation_patient[5]
            rda_file.AddKeyValue("ColumnVector[2]", column_vector2)
        else:
            logging.error("Cannot add RowVector[0][1][2] and ColumnVector[0][1][2]")

        image_position_patient = GetTagValue(dicom_file, 0x00200032)
        if (image_position_patient is not None) and (len(image_position_patient) >= 3):
            #VOIPositionSag, not sure
            voi_position_sag = image_position_patient[0]
            rda_file.AddKeyValue("VOIPositionSag", voi_position_sag)

            #VOIPositionCor
            voi_position_cor = image_position_patient[1]
            rda_file.AddKeyValue("VOIPositionCor", voi_position_cor)

            #VOIPositionTra
            voi_position_tra = image_position_patient[2]
            rda_file.AddKeyValue("VOIPositionTra", voi_position_tra)
        else:
            logging.error("Cannot add VOIPositionSag, VOIPositionCor, VOIPositionTra")

        voi_size = GetTagValue(dicom_file, 0x0065ff05)
        if (voi_size is not None) and (len(voi_size) >= 3):
            #VOIThickness
            voi_thickness = voi_size[2]
            rda_file.AddKeyValue("VOIThickness", voi_thickness)

            #VOIPhaseFOV
            voi_phase_fov = voi_size[1]
            rda_file.AddKeyValue("VOIPhaseFOV", voi_phase_fov)

            #VOIReadoutFOV
            voi_readout_fov = voi_size[0]
            rda_file.AddKeyValue("VOIReadoutFOV", voi_readout_fov)
        else:
            logging.error("Cannot add VOIThickness, VOIPhaseFOV, VOIReadoutFOV")

        voi_normal = GetTagValue(dicom_file, 0x0065ff06)
        if (voi_normal is not None) and (len(voi_normal) >= 3):
            #VOINormalSag
            voi_normal_sag = voi_normal[0]
            rda_file.AddKeyValue("VOINormalSag", voi_normal_sag)
            print "VOINormalSag: %s" % voi_normal_sag

            #VOINormalCor
            voi_normal_cor = voi_normal[1]
            rda_file.AddKeyValue("VOINormalCor", voi_normal_cor)

            #VOINormalTra
            voi_normal_tra = voi_normal[2]
            rda_file.AddKeyValue("VOINormalTra", voi_normal_tra)
        else:
            logging.error("Cannot add VOINormalSag, VOINormalCor, VOINormalTra")

        #VOIRotationInPlane
        voi_rotation_in_plane = GetTagValue(dicom_file, 0x00651013)
        rda_file.AddKeyValue("VOIRotationInPlane", voi_rotation_in_plane)

        fov_size = GetTagValue(dicom_file, 0x0065ff04)
        if (fov_size is not None) and (len(fov_size) >= 3):
            #FoVHeight
            fov_height = fov_size[2]
            rda_file.AddKeyValue("FoVHeight", fov_height)

            #FoVWidth
            fov_width = fov_size[1]
            rda_file.AddKeyValue("FoVWidth", fov_width)

            #FoV3D
            fov_3d = fov_size[0]
            rda_file.AddKeyValue("FoV3D", fov_3d)
        else:
            logging.error("Cannot add FoVHeight, FoVWidth, FoV3D")

        #PercentOfRectFoV
        percent_of_rect_fov = 1.0
        rda_file.AddKeyValue("PercentOfRectFoV", percent_of_rect_fov)

        #NumberOfRows
        number_of_rows = GetTagValue(dicom_file, 0x00280010)
        rda_file.AddKeyValue("NumberOfRows", number_of_rows)

        #NumberOfColumns
        number_of_columns = GetTagValue(dicom_file, 0x00280011)
        rda_file.AddKeyValue("NumberOfColumns", number_of_columns)

        #NumberOf3DParts
        number_of_3d_parts = GetTagValue(dicom_file, 0x00200008)
        rda_file.AddKeyValue("NumberOf3DParts", number_of_3d_parts)

        mrs_pixel_spacing = GetTagValue(dicom_file, 0x0065ff05)
        if (mrs_pixel_spacing is not None) and (len(mrs_pixel_spacing) >= 3):
            #PixelSpacingRow, not sure
            pixel_spacing_row = mrs_pixel_spacing[0]
            rda_file.AddKeyValue("PixelSpacingRow", pixel_spacing_row)

            #PixelSpacingCol
            pixel_spacing_col = mrs_pixel_spacing[1]
            rda_file.AddKeyValue("PixelSpacingCol", pixel_spacing_col)

            #PixelSpacing3D
            pixel_spacing_3d = mrs_pixel_spacing[2]
            rda_file.AddKeyValue("PixelSpacing3D", pixel_spacing_3d)
        else:
            logging.error("Cannot add PixelSpacingRow, PixelSpacingCol, PixelSpacing3D")

        #MRSRawData
        mrs_raw_data = GetTagValue(dicom_file, 0x56000020)
        rda_file.AddKeyValue("MRSRawData", mrs_raw_data)

        logging.info("Exit main func: MRSUIH2RDA successfully.")
    except Exception, e:
        logging.error("errors happen in MRSSiemens2UIH. Error is: %s" % e)

class RDAFile(object):
    """
    RDA file format:

    >>> Begin of header <<<
    PatientName: SPECTR TEST1
    PatientID: 209120611
    PatientSex: M
    *****
    >>> End of header <<<
    Raw MR Spectroscopy data stream
    """
    def __init__(self, file_name):
        self.filename = file_name
        self.keyvalue = []

    def AddKeyValue(self, key, value):
        if value is not None:
            self.keyvalue.append((key, value))
        else:
            logging.warning("The value of key: %s is None." % key)


    def WriteFile(self):
        with open(self.filename, "wb") as rda_file:
            rda_file.write(">>> Begin of header <<<\n")

            for key_value in self.keyvalue[0:-1]:
                rda_file.write(str("%s: %s\n" % (key_value[0], key_value[1])))

            rda_file.write(">>> End of header <<<\n")

            #write mrs data as double stream
            pack_format = "%sd" % len(self.keyvalue[-1][1])
            pack_struct = struct.Struct(pack_format)
            pack_stream = pack_struct.pack(*self.keyvalue[-1][1])
            rda_file.write(pack_stream)

if __name__ == '__main__':
    import os

    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    mrs_rda_file = RDAFile("D:/Project/PythonCode/dicom_converter/U2Srda/test_data/test.rda")

    uih_mrs = dicom.read_file("D:/Project/PythonCode/dicom_converter/U2Srda/test_data/00000001.dcm")

    MRSUIH2RDA(uih_mrs, mrs_rda_file)

    mrs_rda_file.WriteFile()
