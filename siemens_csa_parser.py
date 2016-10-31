#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
this module parses the Siemens CSA header which is a private header with OB(its VR).
refere to the article:  Siemens format DICOM with CSA header.

The CSAImageHeaderInfo and the CSA Series Header Info fields are of the same format. 
The fields can be of two types, CSA1 and CSA2. 
"""

__author__ = 'YANG Chunshan'


import dicom
import logging
import struct

def SiemensCSAHeaderParser(csa_header):
    """
    this function parses Siemens CSA header

    The CSAImageHeaderInfo and the CSA Series Header Info fields are of the same format. The fields can be of two types, CSA1 and CSA2.
    Both are always little-endian, whatever the machine endian is.
    The CSA2 format begins with the string ‘SV10’, the CSA1 format does not.
    """
    logging.info("enter func: SiemensCSAHeaderParser")
    print len(csa_header)

    tag_list = []
    if csa_header[0:4] == "SV10":
        # csa2 header
        tag_list = SiemensCSA2Parser(csa_header)
    else:
        # csa1 header
        tag_list = SiemensCSA1Parser(csa_header)

    logging.info("exit func: SiemensCSAHeaderParser successfully")
    return tag_list

def SiemensCSA1Parser(csa1_header):
    """
    this function parses CSA1 header.
    CSA1

    Start header:
    n_tags, uint32, number of tags. Number of tags should apparently be between 1 and 128. If this is not true we just abort and move to csa_max_pos.
    unused, uint32, apparently has value 77
    
    Each tag:
    name : S64, null terminated string 64 bytes
    vm : int32
    vr : S4, first 3 characters only
    syngodt : int32
    nitems : int32
    xx : int32 - apparently either 77 or 205
    nitems gives the number of items in the tag. The items follow directly after the tag.

    Each item:
    xx : int32 * 4 . The first of these seems to be the length of the item in bytes, modified as below.
    At this point SPM does a check, by calculating the length of this item item_len with xx[0] - the nitems of the first read tag. If item_len is less than 0 or greater than csa_max_pos-csa_position (the remaining number of bytes to read in the whole header) then we break from the item reading loop, setting the value below to ‘’.

    Then we calculate item_len rounded up to the nearest 4 byte boundary tp get next_item_pos.

    value : uint8, item_len.
    We set the stream position to next_item_pos.

    Matlab Code:
    function t = decode_csa1(fp,lim)
    n   = fread(fp,1,'uint32');
    if n>128 | n < 0,
        fseek(fp,lim-4,'cof');
        t = struct('junk','Don''t know how to read this damned file format');
        return;
    end;
    xx  = fread(fp,1,'uint32')'; % "M" or 77 for some reason
    tot = 2*4;
    for i=1:n,
        t(i).name    = fread(fp,64,'char')';
        msk          = find(~t(i).name)-1;
        if ~isempty(msk),
            t(i).name    = char(t(i).name(1:msk(1)));
        else,
            t(i).name    = char(t(i).name);
        end;
        t(i).vm      = fread(fp,1,'int32')';
        t(i).vr      = fread(fp,4,'char')';
        t(i).vr      = char(t(i).vr(1:3));
        t(i).syngodt = fread(fp,1,'int32')';
        t(i).nitems  = fread(fp,1,'int32')';
        t(i).xx      = fread(fp,1,'int32')'; % 77 or 205
        tot          = tot + 64+4+4+4+4+4;
        for j=1:t(i).nitems
             This bit is just wierd
            t(i).item(j).xx  = fread(fp,4,'int32')'; % [x x 77 x]
            len              = t(i).item(j).xx(1)-t(1).nitems;
            if len<0 | len+tot+4*4>lim,
                t(i).item(j).val = '';
                tot              = tot + 4*4;
                break;
            end;
            t(i).item(j).val = char(fread(fp,len,'char'))';
            fread(fp,rem(4-rem(len,4),4),'char')';
            tot              = tot + 4*4+len+rem(4-rem(len,4),4);
        end;
    end;
    return;
    """
    #number of tags. Number of tags should apparently be between 1 and 128.
    num_tags, = struct.unpack("i", csa1_header[0:4])
    logging.info("Number of tags in Siemens CSA1 header is: %s." % num_tags)
    if num_tags > 128 or num_tags < 0:
        raise "Wrong number of tags. Don''t know how to read this damned file format"

    tags_start = 8
    tag_name_len = 64    #null terminated string 64 bytes
    tag_vm_len = 4       #int32
    tag_vr_len = 4       #S4, first 3 characters only
    tag_syngodt_len = 4  #int32
    tag_nitems_len = 4   #int32
    tag_xx_len = 4       #int32
    cursor = tags_start

    tag_list = []
    try:
        for i in range(num_tags):
            tag = {}

            tag_name, = struct.unpack("64s", csa1_header[cursor:cursor + tag_name_len])
            #print tag_name
            tag_name = tag_name.split("\0")[0]
            # print tag_name
            tag["Name"] = tag_name

            cursor = cursor + tag_name_len
            tag_vm, = struct.unpack("i", csa1_header[cursor:cursor+tag_vm_len])
            # print tag_vm
            tag["VM"] = tag_vm

            cursor = cursor + tag_vm_len
            tag_vr, = struct.unpack("4s", csa1_header[cursor: cursor+tag_vr_len])
            tag_vr = tag_vr.split("\0")[0]
            # print tag_vr
            tag["VR"] = tag_vr

            cursor = cursor + tag_vr_len
            tag_syngodt, = struct.unpack("i", csa1_header[cursor:cursor+tag_syngodt_len])
            # print tag_syngodt
            tag["SyngoDT"] = tag_syngodt

            cursor = cursor + tag_syngodt_len
            tag_nitems, = struct.unpack("i", csa1_header[cursor:cursor+tag_nitems_len])
            # print tag_nitems
            tag["NoOfItems"] = tag_nitems

            cursor = cursor + tag_nitems_len
            tag_xx, = struct.unpack("i", csa2_header[cursor:cursor+tag_xx_len])
            # print tag_xx

            cursor = cursor + tag_xx_len

            items = []
            for j in range(tag_nitems):
                item_xx = struct.unpack("4i", csa2_header[cursor:cursor+4*4])
                # print item_xx
                item_len = item_xx[0]
                if i == 0:
                    item_len = item_xx[0] - tag_nitems
                else:
                    item_len = item_xx[0] - tag_list[0]["NoOfItems"]

                cursor = cursor + 4*4

                if item_len < 0 or item_len > csa1_header_len - cursor - 4*4:
                    item_val = ""    
                    break

                str_format = str(item_len) + "s"
                item_val, = struct.unpack(str_format, csa1_header[cursor:cursor+item_len])
                # print item_val
                items.append(item_val)

                cursor = cursor + item_len + ((4 - (item_len % 4)) % 4)


            tag["Data"] = items

            tag_list.append(tag)

        logging.info("Siemens CSA1 header is successfully parsed.")
    except Exception, e:
        logging.error("Errors happen when parsing Siemens CSA1 header. Error is: %s." % e.message)

    return tag_list

def SiemensCSA2Parser(csa2_header):
    """
    this function parses CSA2 header which begins with "SV10"
    CSA2 Header

    Start header:
    hdr_id : S4 == ‘SV10’
    unused1 : uint8, 4
    n_tags: uint32, number of tags. Number of tags should apparently be between 1 and 128. If this is not true we just abort and move to csa_max_pos.
    unused2: uint32, apparently has value 77

    Each tag:
    name : S64, null terminated string 64 bytes
    vm : int32
    vr : S4, first 3 characters only
    syngodt : int32
    nitems : int32
    xx : int32 - apparently either 77 or 205
    nitems gives the number of items in the tag. The items follow directly after the tag.

    Each item:
    xx : int32 * 4 . The first of these seems to be the length of the item in bytes, modified as below.
    Now there’s a different length check from CSA1. item_len is given just by xx[1]. If item_len > csa_max_pos - csa_position (the remaining bytes in the header), then we just read the remaning bytes in the header (as above) into value below, as uint8, move the filepointer to the next 4 byte boundary, and give up reading.

    value : uint8, item_len.

    Matlab Code:
    function t = decode_csa2(fp,lim)
    c   = fread(fp,4,'char');
    n   = fread(fp,4,'char');
    n   = fread(fp,1,'uint32');
    if n>128 | n < 0,
        fseek(fp,lim-4,'cof');
        t = struct('junk','Don''t know how to read this damned file format');
        return;
    end;
    xx  = fread(fp,1,'uint32')'; % "M" or 77 for some reason
    for i=1:n,
        t(i).name    = fread(fp,64,'char')';
        msk          = find(~t(i).name)-1;
        if ~isempty(msk),
            t(i).name    = char(t(i).name(1:msk(1)));
        else,
            t(i).name    = char(t(i).name);
        end;
        t(i).vm      = fread(fp,1,'int32')';
        t(i).vr      = fread(fp,4,'char')';
        t(i).vr      = char(t(i).vr(1:3));
        t(i).syngodt = fread(fp,1,'int32')';
        t(i).nitems  = fread(fp,1,'int32')';
        t(i).xx      = fread(fp,1,'int32')'; % 77 or 205
        for j=1:t(i).nitems
            t(i).item(j).xx  = fread(fp,4,'int32')'; % [x x 77 x]
            len              = t(i).item(j).xx(2);
            t(i).item(j).val = char(fread(fp,len,'char'))';
            fread(fp,rem(4-rem(len,4),4),'char');
        end;
    end;
    return;
    """
    logging.info("enter SiemensCSA2Parser")
    
    #number of tags. Number of tags should apparently be between 1 and 128.
    num_tags, = struct.unpack("i", csa2_header[8:12])
    logging.info("Number of tags in Siemens CSA2 header is: %s." % num_tags)

    if num_tags > 128 or num_tags < 0:
        raise "Wrong number of tags. Don''t know how to read this damned file format"

    tags_start = 16
    tag_name_len = 64    #null terminated string 64 bytes
    tag_vm_len = 4       #int32
    tag_vr_len = 4       #S4, first 3 characters only
    tag_syngodt_len = 4  #int32
    tag_nitems_len = 4   #int32
    tag_xx_len = 4       #int32
    cursor = tags_start

    tag_list = []
    try:
        for i in range(num_tags):
            tag = {}

            tag_name, = struct.unpack("64s", csa2_header[cursor:cursor + tag_name_len])
            tag_name = tag_name.split("\0")[0]
            #print tag_name
            tag["Name"] = tag_name

            cursor = cursor + tag_name_len
            tag_vm, = struct.unpack("i", csa2_header[cursor:cursor+tag_vm_len])
            # print tag_vm
            tag["VM"] = tag_vm

            cursor = cursor + tag_vm_len
            tag_vr, = struct.unpack("4s", csa2_header[cursor: cursor+tag_vr_len])
            tag_vr = tag_vr.split("\0")[0]
            # print tag_vr
            tag["VR"] = tag_vr

            cursor = cursor + tag_vr_len
            tag_syngodt, = struct.unpack("i", csa2_header[cursor:cursor+tag_syngodt_len])
            # print tag_syngodt
            tag["SyngoDT"] = tag_syngodt

            cursor = cursor + tag_syngodt_len
            tag_nitems, = struct.unpack("i", csa2_header[cursor:cursor+tag_nitems_len])
            # print tag_nitems
            tag["NoOfItems"] = tag_nitems

            cursor = cursor + tag_nitems_len
            tag_xx, = struct.unpack("i", csa2_header[cursor:cursor+tag_xx_len])
            # print tag_xx

            cursor = cursor + tag_xx_len

            items = []
            for j in range(tag_nitems):
                item_xx = struct.unpack("4i", csa2_header[cursor:cursor+4*4])
                # print item_xx
                item_len = item_xx[1]
                # print item_len
                cursor = cursor + 4 * 4

                str_format = str(item_len) + "s"
                item_val, = struct.unpack(str_format, csa2_header[cursor:cursor+item_len])
                item_val = item_val.split("\0")[0]
                # print item_val
                items.append(item_val)

                cursor = cursor + item_len + ((4 - (item_len % 4)) % 4)

            tag["Data"] = items

            tag_list.append(tag)

        logging.info("Siemens CSA2 header is successfully parsed.")
    except Exception, e:
        logging.error("Errors happen when parsing Siemens CSA2 header. Error is: %s." % e.message)
    
    return tag_list

if __name__ == '__main__':
    import os

    current_path = os.getcwd()
    logging.basicConfig(level = logging.DEBUG, 
        format='%(asctime)s  %(filename)s  [line:%(lineno)d]  %(levelname)s  %(message)s',
        datefmt='%Y %b %d %H:%M:%S',
        filename = os.path.join(current_path, 'log.txt') , 
        filemode = "w")

    dcm_info = dicom.read_file("D:/Project/PythonCode/dicom_converter/S2U_MRS/S_MRS_test_data/S_CSI.IMA")
    s_csa_header = dcm_info[0x0029, 0x1110].value
    SiemensCSAHeaderParser(s_csa_header)