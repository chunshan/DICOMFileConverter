功能与目的：
This module aims to implement a dicom converter following the config file.
It has two parts. One part is the common dicom converter which can be represented by xml;
the other part is customized which must be implemented by code which can be loaded dynamically 
by the program.

环境准备：
1. 此模块在python2.7环境下开发，需要安装python 2.7
2. 使用pydicom解析dicom文件，需要安装pydicom

使用指南：
1. The example of configuration file:
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

2. If a customized module is necessary, the module(.py file) should be placed in 
the same folder with the configuration file.

And the function in the module should follow the format as below:

the input parameter is an object of DICOM file, so pydicom should be installed 
and dicom module should be imported.

def DICOMConverter(dicom_file):

3.程序运行后会在同目录下生成log.txt的日志文件，如果发生错误可以参考问题发生在哪里

参考例子：
见P2U_DTI下的xml文件和.py文件

TODO List:
1, 增加进度显示，当修改的文件较多时不至于没有任何提示信息；
2，增加图像显示和一个文件的所有tag信息显示；
3，增加UI使得编辑ADD，DELETE和MODIFY的tag信息更加方便，不用直接编辑xml文件；
4，重构代码使得风格更加pythonic
5. 提供更多模板比如UIH2Syngo,Syngo2UIH,UIH2GE, GE2UIH等