#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module implements the conversion of DTI data from Philips to UIH.
This module implements the part which cannot be expressed in the config file. 
"""

__author__ = 'YANG Chunshan'


import dicom
import logging

INSTANCE_NUMBER = 1

def DTIPhilips2UIH(dicom_file):
    """
    this function has 2 functionalities:
    1, make the instance number successive;
    2, add private b0 tag conditionally;
    """
    logging.debug("enter customized func: DTIPhilips2UIH")

    global INSTANCE_NUMBER
    dicom_file.InstanceNumber = str(INSTANCE_NUMBER)
    INSTANCE_NUMBER = INSTANCE_NUMBER + 1

    # 0x00189087 is the public "Diffusion b-value" tag
    if dicom_file.has_key(0x00189087):
        if dicom_file[0x00189087].value == 0:
            dicom_file.add_new(0x0065102D, "ST", "DTI_b0")

if __name__ == '__main__':
    global INSTANCE_NUMBER
    print INSTANCE_NUMBER