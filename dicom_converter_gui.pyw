#! /usr/bin/env python
# -*- coding:utf8 -*-

import wx
from wx.lib.scrolledpanel import ScrolledPanel
import os,sys
import glob
import time
import dicom
from GenericDispatch import GenericDispatchMix
import threading
from dicom_converter_ui import SeriesDicomConverter  

def getControlFont(type):
    '''get the specific font for the specific type of control
    [param][in] type:the control type
    '''
    if type == 'st':
        font = wx.Font(10,wx.SWISS,wx.NORMAL,wx.BOLD,True)       
    elif type == 'btn':
        font = wx.Font(8,wx.ROMAN,wx.NORMAL,wx.NORMAL)
    return font

class TRun_GUI_DICOM_Convert(threading.Thread):
    """A child thread class to update the progress bar when doing dicom convert of series"""
    def __init__(self,caller,series_index_list,threadName='DICOM Convert Progress Update'):
        """ [param][in] caller:the SeriesDicomConverterFrame object
        """
        threading.Thread.__init__(self,name=threadName)
        self.caller = caller
        self.series_index_list = series_index_list         
       
    
    def update(self):
        """update the progress bar when doing dicom convert"""
        value = self.caller.t_convert_run.getFinishedFilesInCurrSeries() 
        allValue = self.caller.t_convert_run.getFinishedSeiresNumber()
        # update the label
        index = self.caller.t_convert_run.getFinishedSeiresNumber()
        if index < len(self.series_index_list):
            series_index = self.series_index_list[index] + 1                   
            self.caller.setCurrentSeriesIndex(series_index)
            self.caller.t_convert_run.setTagToContinue()        
        
        self.caller.update(value,allValue)
        self.caller.Refresh()        

    def run(self):
        while True:
            if self.caller.t_convert_run.isCurrSeriesConvertFinished():               
                self.caller.ThreadSafeDispatch(self.update)
                
            if self.caller.t_convert_run.isAllSeriesConvertFinished():
                self.caller.ThreadSafeDispatch(self.update)
                break
            self.caller.ThreadSafeDispatch(self.update)
            time.sleep(1)


class SeriesDicomConvertProgressPanel(wx.Panel,GenericDispatchMix):
    '''a panel for display the dicom convert progress'''
    def __init__(self,parent,size,series_convert_paras,series_id_list,series_index_list,id=-1):
        wx.Panel.__init__(self,parent,id)
        GenericDispatchMix.__init__(self)
        self.SetSize(size)
        self.series_convert_paras = series_convert_paras        
        self.series_id_list = series_id_list        
        self.series_index_list = series_index_list
        self.GUI_init()
        
    def GUI_init(self):
        font_st = getControlFont('st')
        self.st_curr_series = wx.StaticText(self,-1,u'当前序列:',style=wx.TE_CENTER)
        self.st_curr_series.SetFont(font_st)
        self.st_curr_series.SetBackgroundColour('White')
        self.st_curr_series.SetForegroundColour('Black')
        
        # the progress bar when converting the current series
        size = (self.ClientSize.x,20)
        self.progressBar_curr_series = wx.Gauge(self,-1,100,size=size, style=wx.GA_PROGRESSBAR|wx.ALIGN_CENTER)
        self.progressBar_curr_series.SetBezelFace(3)
        self.progressBar_curr_series.SetShadowWidth(3)
        self.progressBar_curr_series.Show(False)
        
        st_total_series = wx.StaticText(self,-1,u'全部序列:',style=wx.TE_CENTER)
        st_total_series.SetFont(font_st)
        st_total_series.SetBackgroundColour("White")
        st_total_series.SetForegroundColour('Black')
        
        # the progress bar when converting all series
        self.progressBar_all_series = wx.Gauge(self,-1,100,size=size, style=wx.GA_PROGRESSBAR|wx.ALIGN_CENTER)
        self.progressBar_all_series.SetBezelFace(3)
        self.progressBar_all_series.SetShadowWidth(3)
        self.progressBar_all_series.Show(False)
        
        self.flex_sizer = wx.FlexGridSizer(cols=2,hgap=10,vgap=40)       
        self.flex_sizer.Add(self.st_curr_series,0,wx.ALIGN_CENTER)
        self.flex_sizer.Add(self.progressBar_curr_series,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flex_sizer.AddStretchSpacer()
        self.flex_sizer.AddStretchSpacer()
        self.flex_sizer.Add(st_total_series,0,wx.ALIGN_CENTER)
        self.flex_sizer.Add(self.progressBar_all_series,0,wx.ALIGN_TOP|wx.EXPAND)
        
        self.SetSizer(self.flex_sizer)
        self.flex_sizer.Fit(self)
        self.Center()       
        
    def setCurrentSeriesIndex(self,index):
        '''set and update the current series index'''       
        self.st_curr_series.SetLabel(u"当前序列%d:" %index)
    
    def setCurrentProgressBarRange(self,value):
        '''set the range of current progress bar'''
        self.progressBar_curr_series.SetRange(value)
    
    def setAllProgressBarRange(self,value):
        '''set the range of all progress bar'''
        self.progressBar_all_series.SetRange(value)
    
    def update(self,currValue,allValue):
        '''update the two progress bar'''
        self.progressBar_curr_series.SetValue(currValue)
        self.progressBar_all_series.SetValue(allValue)
        self.flex_sizer.Fit(self)
        self.flex_sizer.Layout()
    
    def run(self):
        '''the main loop to control the whole convert procedure for all series'''
        # gui update thread
        self.t_pggui_run = TRun_GUI_DICOM_Convert(self,self.series_index_list)
        print 'series index list size = ',len(self.series_index_list)
        self.setAllProgressBarRange(len(self.series_index_list))        
        
        print 'series convert paras = ',self.series_convert_paras
        self.t_convert_run = SeriesDicomConverter(self.series_convert_paras,self.series_id_list)
        numFiles = self.t_convert_run.getTotalFilesInCurrSeries()
        
        self.setCurrentProgressBarRange(numFiles)        
        # set label
        index = self.series_index_list[0] + 1
        self.setCurrentSeriesIndex(index)
        
        self.progressBar_curr_series.Show()
        self.progressBar_all_series.Show()
        
        # set initial progress
        self.update(0,0)
        
        # start threads to update
        self.t_pggui_run.setDaemon(True)
        self.t_pggui_run.start()
        
        self.t_convert_run.setDaemon(True)
        self.t_convert_run.start()
        

class SeriesDicomConverterPanel(wx.Panel):
    '''a customized panel for dicom convert definition for each series
    '''    
    def __init__(self,parent,size,dst_data_path,dicom_file_name,id=-1,seriesIndex=1,seriesIndexList=None):
        wx.Panel.__init__(self,parent,id)
        self.index = seriesIndex
        self.seriesIndexList = seriesIndexList
        self.type = 0
        self.dicom_file_name = dicom_file_name
        self.dst_data_path = dst_data_path
        self.SetSize(size)                         
        self.GUI_init()
        
    
    def GUI_init(self):
        '''GUI init to construct a customized panel'''         
        self.panel_head = SeriesDicomConverterCommonHeadPanel(self,-1,self.index)
        self.panel_head.Show()
        self.Bind(EVT_CONVERT_TYPE_CHANGE,self.OnConvertTypeChange,self.panel_head)  
 
                
        type = self.panel_head.getConvertType()
        if type == 0: # convert by GUI setting
            self.dicom_convert_panel = SeriesDicomConverterGUIPanel(self,self.dicom_file_name,-1)
            # response to GUI update
            self.Bind(EVT_DICOM_TAG_CHANGE,self.OnUpdate)         
        else: # convert by config file           
            self.dicom_convert_panel = SeriesDicomConverterConfigFilePanel(self,-1)
            

        self.panel_tail = SeriesDicomConverterTailPanel(self,-1)

        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v.Add(self.panel_head,0,wx.ALL|wx.ALIGN_TOP,10)
        self.box_sizer_v.AddSpacer(20)             
        self.box_sizer_v.Add(self.dicom_convert_panel,1,wx.ALL|wx.EXPAND,10)
        self.box_sizer_v.AddStretchSpacer()
        self.box_sizer_v.Add(self.panel_tail,0,wx.ALL|wx.ALIGN_BOTTOM,10)       
        
        self.SetSizer(self.box_sizer_v)
        self.box_sizer_v.Fit(self)
        self.Center()
        
    def getConvertType(self):
        return self.type
    
    def getCurrentSeriesIndex(self):
        return self.index
    
    def getSelectedConfigFileName(self):
        return self.dicom_convert_panel.getConvertConfigFile()
    
    def Now(self):
        return time.strftime('%Y%m%d',time.localtime(time.time()))
    
    def getNewConfigFileName(self):
        '''get the new config file name.
           name=dst_data_path+seriesid+filename
        '''
        # get the series instance id
        dfile = dicom.read_file(self.dicom_file_name)
        series_instance_id = dfile.SeriesInstanceUID 
        file_path = self.dst_data_path + os.sep + self.Now()
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        file_name = file_path + os.sep + "%s.xml" %series_instance_id
        return file_name 
    
    def isAllSeriesConvertDefined(self):
        if (self.index - 1) == self.seriesIndexList[-1]:
            return True
        return False
        
    
    def isConvertTagsNotEmpty(self):
        '''check if there is any tags to convert'''
        num_tags = 0
        if self.type == 0: # GUI
            lsTags = self.dicom_convert_panel.getAddTagElements()
            num_tags += len(lsTags)
            lsTags = self.dicom_convert_panel.getDelTagElements()
            num_tags += len(lsTags)
            lsTags = self.dicom_convert_panel.getModTagElements()
            num_tags += len(lsTags)
            lsTags = self.dicom_convert_panel.getCusTagElements() 
            num_tags += len(lsTags)
            if num_tags > 0:
                return True
            return False
        else: # Config file
            return self.dicom_convert_panel.isConvertConfigFileValid()
        
    def createDicomConvertConfigFile(self,filename,title):
        '''create the config file with the tags input'''
        lsTags = self.dicom_convert_panel.getAddTagElements()
        wf = open(filename,'w')
        wf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        wf.write('<Converter Title = "%s">\n' %title)
        wf.write('   <ADD>\n')
        for tag in lsTags:
            if tag.has_key('Value'):
                wf.write('      <Tag ID="%s" VR="%s" Value="%s"/>\n' %(tag["ID"],tag["VR"],tag["Value"]))
            else:
                wf.write('      <Tag ID="%s" VR="%s" ReferenceTagID="%s" ReferenceTagVR="%s"/>\n' %(tag["ID"],tag["VR"],tag["ReferenceTagID"],tag["ReferenceTagVR"]))
                  
        wf.write('   </ADD>\n')
        
        lsTags = self.dicom_convert_panel.getDelTagElements()
        wf.write('  <DELETE>\n')
        for tag  in lsTags:
            wf.write('      <Tag ID="%s"/>\n' %tag["ID"])
        wf.write('   </DELETE>\n')
        
        lsTags = self.dicom_convert_panel.getModTagElements()
        wf.write('   <MODIFY>\n')
        for tag in lsTags:
            if tag.has_key('Value'):
                wf.write('      <Tag ID="%s" VR="%s" Value="%s"/>\n' %(tag["ID"],tag["VR"],tag["Value"]))
            else:
                wf.write('      <Tag ID="%s" VR="%s" ReferenceTagID="%s" ReferenceTagVR="%s"/>\n' % (tag["ID"],tag["VR"],tag["ReferenceTagID"],tag["ReferenceTagVR"]))
        wf.write('   </MODIFY>\n')
        
        lsTags = self.dicom_convert_panel.getCusTagElements()
        if len(lsTags) > 0:
            wf.write('   <CUSTOMIZED>\n')
            for tag in lsTags:
                wf.write('      <ModuleName>%s</ModuleName>\n' %tag["ModuleName"])
                wf.write('      <FunctionName>%s</FunctionName>\n' %tag["FunctionName"])
            wf.write('   </CUSTOMIZED>\n')
            
        wf.write('</Converter>\n')
        wf.close()               
                
            
    
    def newDicomConvertPanel(self,type):
        '''a factory method to produce different type of panel'''
        if type == 1:
            panel = SeriesDicomConverterConfigFilePanel(self,-1)
        else:
            panel = SeriesDicomConverterGUIPanel(self,self.dicom_file_name,-1)            
        return panel
    
    def OnUpdate(self,event):
        '''event handler for GUI update'''        
        self.dicom_convert_panel.Refresh()
    
    def OnConvertTypeChange(self,event):
        '''event handler for dicom convert type changed'''
        type = event.getConvertType()        
        if type != self.type:
            self.type = type           
            # first remove the previous panel
            self.box_sizer_v.Remove(self.dicom_convert_panel)
            self.dicom_convert_panel.Hide()                      
            # then insert the new panel
            self.dicom_convert_panel = self.newDicomConvertPanel(type)            
            self.box_sizer_v.Insert(2,self.dicom_convert_panel,0,wx.ALL|wx.EXPAND,10)                       
            self.box_sizer_v.Layout() 
        event.Skip()
           
            

class DicomConvertTypeEvent(wx.PyCommandEvent):
    def __init__(self,evtType,id):
        wx.PyCommandEvent.__init__(self,evtType,id)
        self.convert_type = 0   # 0:by config file;1:by gui
        
    def getConvertType(self):
        return self.convert_type
    
    def setConvertType(self,type):
        self.convert_type = type
        
# define an event type
myEVT_CONVERT_TYPE_CHANGE = wx.NewEventType()
# define an event binder
EVT_CONVERT_TYPE_CHANGE = wx.PyEventBinder(myEVT_CONVERT_TYPE_CHANGE,1)        
    

class SeriesDicomConverterCommonHeadPanel(wx.Panel):
    '''define a common panel as the head at the series dicom convert panel'''
    def __init__(self,parent,id=-1,index=1):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,40))        
        self.index = index
        self.convert_type = 0 # 0:by config file;1:by gui         
        self.GUI_init()
    
    def GUI_init(self):
        # font for static text
        font_st = getControlFont('st')
        # font for button lable
        font_btn = getControlFont('btn')
                
        st_cap = wx.StaticText(self,-1,u'序列:%d' %self.index,style=wx.TE_CENTER)
        st_cap.SetFont(font_st)
        st_cap.SetBackgroundColour("White")
        st_cap.SetForegroundColour('Black')        
                
        # list of convert type
        series_convert_type = [u'手动输入转换项',u'按现有配置文件转换']       
        # radio box to select convert type
        self.radio_convert_type = wx.RadioBox(self,-1,u'转换类型',wx.DefaultPosition,wx.DefaultSize,series_convert_type,1,wx.RA_SPECIFY_ROWS)
        self.Bind(wx.EVT_RADIOBOX,self.OnSelConvertType,self.radio_convert_type)
        
        self.box_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_h.Add(st_cap,1,wx.ALL|wx.ALIGN_CENTER,border=10)
        self.box_sizer_h.AddStretchSpacer()
        self.box_sizer_h.AddStretchSpacer()
        self.box_sizer_h.AddStretchSpacer()
        self.box_sizer_h.Add(self.radio_convert_type,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.SetSizer(self.box_sizer_h)
        self.box_sizer_h.Fit(self)
        self.Center()    
        
    def getConvertType(self):
        return self.convert_type   
     
    def OnSelConvertType(self,event):
        '''select the radio button for convert type'''
        index = self.radio_convert_type.GetSelection()
        if index == 0: # by config file
            self.convert_type = index           
            # send an event to parent panel to display different dicom convert panel
            # new a event instance and process it
            evt = DicomConvertTypeEvent(myEVT_CONVERT_TYPE_CHANGE,self.GetId())
            evt.setConvertType(0)
            self.GetEventHandler().ProcessEvent(evt)            
        else: # by gui
            self.convert_type = index         
            evt = DicomConvertTypeEvent(myEVT_CONVERT_TYPE_CHANGE,self.GetId())
            evt.setConvertType(1)
            self.GetEventHandler().ProcessEvent(evt)


class SeriesDicomConvertDefinedEvent(wx.PyCommandEvent):
    '''event indicating the series dicom convert is defined'''
    def __init__(self,evtType,id):
        wx.PyCommandEvent.__init__(self,evtType,id)
        self.filename = ""
        self.index = -1
        self.apply_for_remained = False
        self.completed = False
    
    def setFileName(self,filename):
        self.filename = filename
    
    def setIndex(self,index):
        self.index = index
    
    def setApplyTag(self,bApply):
        self.apply_for_remained = bApply
    
    def setCompleteTag(self,bFinish):
        self.completed = bFinish
    
    def getTurpleValue(self):
        return (self.filename,self.index,self.apply_for_remained,self.completed)
        
# define an event type for DICOM convert defined
myEVT_DICOM_CONVERT_DEFINE = wx.NewEventType()
# define an event binder
EVT_DICOM_CONVERT_DEFINE = wx.PyEventBinder(myEVT_DICOM_CONVERT_DEFINE,1)



class SeriesDicomConverterTailPanel(wx.Panel):
    '''define a panel for the tail panel for series dicom convert panel'''
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,60))
        self.dicom_convert_panel = parent                             
        self.GUI_init()
    
    def GUI_init(self):      
        font_btn = getControlFont('btn')        
        
        panel_1 = wx.Panel(self,-1)        
        self.okBtn_series = wx.Button(panel_1,-1,label=u'确定转换',size=(100,30))
        self.okBtn_series.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnOKSeries,self.okBtn_series)
        self.okBtn_series.Enable() 
                
        self.cancelTransBtn_series = wx.Button(panel_1,-1,label=u'取消转换',size=(100,30))
        self.cancelTransBtn_series.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnCancelTransSeries,self.cancelTransBtn_series)
        self.cancelTransBtn_series.Enable()       
        
        self.box_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        self.box_sizer_h.Add(self.okBtn_series,0,wx.ALL|wx.ALIGN_TOP)
        self.box_sizer_h.AddSpacer(30)       
        self.box_sizer_h.Add(self.cancelTransBtn_series,0,wx.ALL|wx.ALIGN_TOP)
        
        panel_1.SetSizer(self.box_sizer_h)
        self.box_sizer_h.Fit(panel_1)
        panel_1.Center()          
       
        flex_sizer = wx.FlexGridSizer(cols=2,hgap=10,vgap=40)
        flex_sizer.Add(panel_1,0,wx.ALL|wx.ALIGN_TOP)
        flex_sizer.AddStretchSpacer()        

        self.SetSizer(flex_sizer)
        flex_sizer.Fit(self)
        self.Center()    
    
    
    def OnOKSeries(self,event):
        '''convert the current series according to the current settings'''  
        # check if the tags can be converted(not empty,or the config file is selected)
        filename = None
        if self.dicom_convert_panel.isConvertTagsNotEmpty():
            if self.dicom_convert_panel.getConvertType() == 0:
                # input the title for new config file
                dialog = wx.TextEntryDialog(None,'Please input the title for config file:','Enter Title','',style=wx.OK|wx.CANCEL)
                if dialog.ShowModal() == wx.ID_OK:
                    title = dialog.GetValue().strip()
                    # create a new config file from the GUI settings
                    filename = self.dicom_convert_panel.getNewConfigFileName()
                    self.dicom_convert_panel.createDicomConvertConfigFile(filename,title)
                dialog.Destroy()
            else:
                # get the selected config file
                filename = self.dicom_convert_panel.getSelectedConfigFileName()
            
            if filename is not None:
                index = self.dicom_convert_panel.getCurrentSeriesIndex() - 1
                # to send an event to notify that the current series convert is defined
                evt = SeriesDicomConvertDefinedEvent(myEVT_DICOM_CONVERT_DEFINE,self.GetId())
                evt.setFileName(filename)
                evt.setIndex(index)
                # confirm if apply for the remained series
                if not self.dicom_convert_panel.isAllSeriesConvertDefined():
                    if wx.MessageBox(u"是否将当前序列的转换规则应用于后续序列?","Yes Or No...",style=wx.YES|wx.NO|wx.ICON_QUESTION) == wx.YES:
                        evt.setApplyTag(True)
                    else:
                        evt.setApplyTag(False)
                    evt.setCompleteTag(False)
                else:
                    evt.setApplyTag(False)
                    evt.setCompleteTag(True)
                self.GetEventHandler().ProcessEvent(evt) 
        else:
            wx.MessageBox(u"请选择配置文件或手动设置转换规则!",u"友情提示")
                 
    
    def OnCancelTransSeries(self,event):
        if wx.MessageBox(u"是否放弃对当前序列的转换?","Yes Or No...",style=wx.YES|wx.NO|wx.ICON_QUESTION) == wx.YES:
            evt = SeriesDicomConvertDefinedEvent(myEVT_DICOM_CONVERT_DEFINE,self.GetId())
            evt.setFileName(None)
            index = self.dicom_convert_panel.getCurrentSeriesIndex() - 1
            evt.setIndex(index)
            if not self.dicom_convert_panel.isAllSeriesConvertDefined():
                evt.setCompleteTag(False)
            else:
                evt.setCompleteTag(True)
            evt.setApplyTag(False)
            self.GetEventHandler().ProcessEvent(evt) 
    
class SeriesDicomConverterConfigFilePanel(wx.Panel):
    '''define a panel to load the config file for series dicom convert'''
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,200)) 
        self.config_file_check_passed = False      
        self.GUI_init()
    
    def GUI_init(self):
        # font for static text
        font_st = getControlFont('st')
        # font for button lable
        font_btn = getControlFont('btn')
        
        st_file_path = wx.StaticText(self,-1,u'配置文件路径:',style=wx.TE_CENTER)
        st_file_path.SetFont(font_st)
        st_file_path.SetBackgroundColour("White")
        st_file_path.SetForegroundColour('Black')
        
        size = wx.Size(self.ClientSize.x/2,10)      
        self.textCtrl_file_path = wx.TextCtrl(self,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
        self.Bind(wx.EVT_TEXT,self.OnFilePathEnter,self.textCtrl_file_path)
        
        browseBtn_file = wx.Button(self,-1,label=u'浏览...',size=(100,30))
        browseBtn_file.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnConfigFileBrowser,browseBtn_file) 
        
        self.cancelBtn = wx.Button(self,-1,label=u'取消选择',size=(100,30))
        self.cancelBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.cancelBtn)
        self.cancelBtn.Enable(False)
        
                
        self.flexSizer = wx.FlexGridSizer(cols=3,hgap=10,vgap=40)       
        self.flexSizer.Add(st_file_path,0,wx.ALIGN_CENTER)
        self.flexSizer.Add(self.textCtrl_file_path,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer.Add(browseBtn_file,0,wx.ALIGN_TOP)
        self.flexSizer.Add(self.cancelBtn,0,wx.ALIGN_TOP)
         
        self.SetSizer(self.flexSizer)
        self.flexSizer.Fit(self)
        self.Center()
    
    def isConvertConfigFileValid(self):
        return self.config_file_check_passed
    
    def OnCancel(self,event):
        '''just clear the file text box'''
        self.textCtrl_file_path.Clear() 
    
    def getConvertConfigFile(self):
        return self.filename_config
        
    def OnFilePathEnter(self,event):
        '''check if the config file is valid or not'''
        filename_config = self.textCtrl_file_path.GetValue().strip() 
        if len(filename_config) == 0:
            self.config_file_check_passed = False
            self.cancelBtn.Enable(False)
        elif self.fileValidCheck(filename_config) == False:
            self.textCtrl_file_path.Clear()
            self.textCtrl_file_path.SetFocus()
            self.config_file_check_passed = False
            self.cancelBtn.Enable(False)            
        else:
            self.config_file_check_passed = True
            self.filename_config = filename_config  
            self.cancelBtn.Enable()          
    
    def fileValidCheck(self,filename):
        # check if the file existed
        if not os.path.exists(filename):
            message = u"文件:%s 不存在!" %filename
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        # check if the file extension is *.xml
        extension = filename.split('.')[-1].strip()
        if extension != 'xml':
            message = u"文件扩展名应该是.xml，实际扩展名为.%s!" %extension
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        return True        
    
    def OnConfigFileBrowser(self,event):
        filename_config = wx.FileSelector(u'选择一个序列DICOM转换规则的配置文件',default_path='',default_filename='',\
                                 default_extension='',wildcard="XML files(*.xml)|*.xml|All files(*.*)|*.*",parent=self)
        if len(filename_config) >0 and self.fileValidCheck(filename_config):
            self.textCtrl_file_path.Clear()
            self.textCtrl_file_path.AppendText(filename_config)
            self.config_file_check_passed = True            
            self.cancelBtn.Enable()
        else:
            self.config_file_check_passed = False            
            self.cancelBtn.Enable(False)

class DicomTagChangeEvent(wx.PyCommandEvent):
    '''event indicating some tag item is added or removed at GUI'''
    def __init__(self,evtType,id):
        wx.PyCommandEvent.__init__(self,evtType,id)   
        
# define an event type for GUI update
myEVT_DICOM_TAG_CHANGE = wx.NewEventType()
# define an event binder
EVT_DICOM_TAG_CHANGE = wx.PyEventBinder(myEVT_DICOM_TAG_CHANGE,1)

            
class AddModifyDeleteTagPanel(wx.Panel):
    '''provide the panel to add or modify or delete tags one by one.
       can be in value mode or reference mode.
    '''
    def __init__(self,parent,id=-1,op='+',tag_id_list=None):
        wx.Panel.__init__(self,parent,id)
        self.SetSize(parent.GetSize())        
        self.mode_by_value = True
        self.op = op
        self.tag_id_list = tag_id_list        
        self.GUI_init()
    
    def GUI_init(self):
        font_st = getControlFont('st')
        font_btn = getControlFont('btn')
        
        self.panel_head = wx.Panel(self,-1)
        
        # radio button by value mode or by reference mode
        # list of mode type
        convert_mode_type = [u'Value',u'Reference']       
        self.radio_convert_mode = wx.RadioBox(self.panel_head,-1,u'转换模式',wx.DefaultPosition,wx.DefaultSize,convert_mode_type,1,wx.RA_SPECIFY_ROWS)
        self.Bind(wx.EVT_RADIOBOX,self.OnSelConvertMode,self.radio_convert_mode)
        
        if self.op == '-': # remove
            self.radio_convert_mode.Hide()
        
        # add button to process possible multiple tags
        self.addBtn = wx.Button(self.panel_head,-1,label=u'+',size=(40,20))
        self.addBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnAdd,self.addBtn)
        
        # sizer to manage the layout
        self.flexSizer = wx.FlexGridSizer(cols=2,hgap=10,vgap=10)       
        self.flexSizer.Add(self.radio_convert_mode,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.flexSizer.Add(self.addBtn,0,wx.ALL|wx.ALIGN_CENTER,border=10)
        
        self.panel_head.SetSizer(self.flexSizer)
        self.flexSizer.Fit(self.panel_head)
        self.panel_head.Center()
        
        self.scrollPanel = AddModifyDeleteTagScrollPanel(self,-1,self.op,self.tag_id_list) 
              
        
        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v.Add(self.panel_head,0,wx.ALL|wx.EXPAND,border=10)
        self.box_sizer_v.Add(self.scrollPanel,1,wx.ALL|wx.EXPAND,border=10)
        self.SetSizer(self.box_sizer_v)        
        self.box_sizer_v.Fit(self)
        self.Center() 
        
    def getTagElements(self):
        return self.scrollPanel.getTagElements()
    
    def OnSelConvertMode(self,event):
        '''select the convert mode for each tag.
           1.by value
           2.by reference
        '''
        index = self.radio_convert_mode.GetSelection()    
        if index == 0:
            self.mode_by_value = True
        else:
            self.mode_by_value = False
            
    def Refresh(self):
        self.flexSizer.Fit(self.panel_head)
        self.flexSizer.Layout()
        self.panel_head.Center()
        self.box_sizer_v.Fit(self)
        self.box_sizer_v.Layout()
        self.Center()

    def OnAdd(self,event):
        '''when clicked,one tag will be added to edit.
           the edit mode is determinated by the convert mode.
        '''
        self.scrollPanel.add(self.mode_by_value)
        self.Refresh()
        self.Center()
        # send out an event for GUI update
        evt = DicomTagChangeEvent(myEVT_DICOM_TAG_CHANGE,self.GetId())
        self.GetEventHandler().ProcessEvent(evt)            
        

class AddModifyDeleteTagScrollPanel(wx.ScrolledWindow):
    '''provide a scrolled panel to add or modify or delete tags one by one'''
    def __init__(self,parent,id=-1,op='+',tag_id_list=None):
        wx.ScrolledWindow.__init__(self,parent,id,style=wx.HSCROLL)       
        self.SetSize((parent.ClientSize.x/1,parent.ClientSize.y/2))        
        self.op = op
        self.tag_id_list = tag_id_list       
        self.items_number = 0
        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)          
        self.SetSizer(self.box_sizer_v)                           
        self.items_undo = {}
        self.items_list = []
        
    def add(self,isByValue):
        '''add a tag element for add/modify
        [param][in] isByValue:the tag is add/modify by value or by reference
                    True:by value;False:by reference
        '''            
        self.items_number += 1
        panel = wx.Panel(self,-1)
        panel.SetSize((320,100))
        
        if self.op != '-': # add or modify
            if isByValue:
                panel_tag = AddModifyTagByValuePanel(panel,-1,self.op,self.tag_id_list)
            else:
                panel_tag = AddModifyTagByReferenceTagPanel(panel,-1,self.op,self.tag_id_list)
        else: # remove
            panel_tag = DeleteTagPanel(panel,-1,self.tag_id_list)
        
        self.items_list.append(panel_tag)
        # attach a remove button 
        removeBtn = wx.Button(panel,-1,label=u'X',size=(20,20))
        id = removeBtn.GetId()            
        self.Bind(wx.EVT_BUTTON,self.OnUndo,removeBtn)
    
        box_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer_h.Add(panel_tag,1,wx.ALL|wx.EXPAND,border=5)
        box_sizer_h.AddSpacer(5)
        box_sizer_h.Add(removeBtn,0,wx.ALL|wx.EXPAND,border=5)
        panel.SetSizer(box_sizer_h)
        box_sizer_h.Fit(panel)
        box_sizer_h.Layout()           
        panel.Center()                  
        
        # record the panel which may be deleted
        self.items_undo[id] = panel
        self.box_sizer_v.Add(panel,0,wx.ALL|wx.EXPAND,border=10)            
        self.box_sizer_v.Fit(self)          
 
        if self.items_number == 7:
            self.box_sizer_v.SetMinSize((400,200))
            self.box_sizer_v.Fit(self)
            self.box_sizer_v.Layout() 
            self.SetVirtualSize((400,200))               
            self.SetScrollRate(0,1)              
                                     
        self.box_sizer_v.Layout()            
        self.Center()
        
    def getTagElements(self):
        lsTags = []
        for item in self.items_list:
            tag_element = item.getTagElement()
            if tag_element is not None:
                lsTags.append(tag_element)
        return lsTags

     
    def OnUndo(self,event):
        '''undo the edit'''
        id = event.GetId()
        items_remove = self.items_undo.pop(id,None)
        if items_remove is not None:
            self.box_sizer_v.Remove(items_remove)
            items_remove.Hide()
            self.box_sizer_v.Fit(self)
            self.box_sizer_v.Layout()
            self.items_list.remove(items_remove.GetChildren()[0])              
            
            # send out an event for GUI update
            evt = DicomTagChangeEvent(myEVT_DICOM_TAG_CHANGE,self.GetId())
            self.GetEventHandler().ProcessEvent(evt)      
   
   
class AddModifyTagByValuePanel(wx.Panel):
    '''provide the panel to add or modify one tag by value'''
    def __init__(self,parent,id=-1,op='+',tag_id_list=None):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,20))        
        self.op = op
        self.ID = ''
        self.VR = ''
        self.Value = ''
        self.tag_id_list = tag_id_list
        self.tag_id_is_valid = False
        self.DICOM_VR = ["AE", "AS", "AT", "CS", 
        "DA", "DS", "DT", "FL", 
        "FD", "IS", "LO", "LT", 
        "OB", "OF", "OW", "PN",
        "SH", "SL", "SQ", "SS",
        "ST", "TM", "UI", "UL",
        "UN", "US", "UT"]

        self.GUI_init()
        
    def GUI_init(self):
        font_st = getControlFont('st')       
        
        # tag id
        st_tag_id = wx.StaticText(self,-1,u'Tag ID:',style=wx.TE_CENTER)
        st_tag_id.SetFont(font_st)
        st_tag_id.SetBackgroundColour("White")
        st_tag_id.SetForegroundColour('Black')
        
        
        size = wx.Size(self.ClientSize.x/4,20)
        
        # if op = add,then just input tag id
        # if op = modify,then allow to select from droplist
        if self.op == '+':
            self.tag_id_control = wx.TextCtrl(self,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
            self.Bind(wx.EVT_TEXT_ENTER,self.OnTagIDEnter,self.tag_id_control)
        else:
            self.tag_id_control = wx.ComboBox(self,-1,choices=self.tag_id_list,style=wx.wx.CB_READONLY|wx.CB_SORT)
            self.Bind(wx.EVT_COMBOBOX,self.OnTagIDEnter,self.tag_id_control)           

        # tag vr,current version with no verification between vr and value
        st_tag_vr = wx.StaticText(self,-1,u'VR:',style=wx.TE_CENTER)
        st_tag_vr.SetFont(font_st)
        st_tag_vr.SetBackgroundColour("White")
        st_tag_vr.SetForegroundColour('Black')
        
        self.comboBoxVR = wx.ComboBox(self,-1,choices=self.DICOM_VR,style=wx.CB_SORT|wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnComboxVRClick,self.comboBoxVR)
        
        # tag value
        st_tag_value = wx.StaticText(self,-1,u'Value:',style=wx.TE_CENTER)
        st_tag_value.SetFont(font_st)
        st_tag_value.SetBackgroundColour("White")
        st_tag_value.SetForegroundColour('Black')
        
        self.textCtrl_tag_value = wx.TextCtrl(self,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
        self.Bind(wx.EVT_TEXT,self.OnTagValueEnter,self.textCtrl_tag_value)
        
        box_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer_h.Add(st_tag_id,0,wx.ALIGN_CENTER)
        box_sizer_h.AddSpacer(10)       
        box_sizer_h.Add(self.tag_id_control,0,wx.ALIGN_TOP|wx.EXPAND)
        box_sizer_h.AddSpacer(10) 
        box_sizer_h.Add(st_tag_vr,0,wx.ALIGN_CENTER)
        box_sizer_h.AddSpacer(10)        
        box_sizer_h.Add(self.comboBoxVR,0,wx.ALIGN_TOP)
        box_sizer_h.AddSpacer(10)         
        box_sizer_h.Add(st_tag_value,0,wx.ALIGN_CENTER)
        box_sizer_h.AddSpacer(10)      
        box_sizer_h.Add(self.textCtrl_tag_value,0,wx.ALIGN_TOP|wx.EXPAND)
        self.SetSizer(box_sizer_h)
        box_sizer_h.Fit(self)
        self.Center()

    def OnTagIDEnter(self,event):
        '''check if the tag id is in such form:0x00080070'''
        id = self.tag_id_control.GetValue().strip().lower()        
        # transform from (xxxx,xxxx) to '0xxxxxxxxx'
        if self.op != '+':
            ls_id = id.split(', ')            
            id = '0x' + ls_id[0][1:] + ls_id[1][:-1]            
        if not id.startswith('0x'):
            message = u"Tag ID:%s 应以0x开头!" %id
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            self.tag_id_control.Clear()
            self.tag_id_is_valid = False            
        else:
            tag_id = id[2:]
            if len(tag_id) != 8:
                message = u"Tag ID:%s 在0x之后应有8位!" %id
                wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                self.tag_id_control.Clear()
                self.tag_id_is_valid = False  
            else:
                try:
                    int(tag_id,16)
                    self.ID = id
                    self.tag_id_is_valid = True  
                except ValueError:
                    message = u"Tag ID:%s 不是有效的16进制!" %id
                    wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                    self.tag_id_control.Clear()
                    self.tag_id_is_valid = False        

    def OnComboxVRClick(self,event):
        '''select tag vr from the droplist'''
        self.VR = self.comboBoxVR.GetValue().strip()
    
    def OnTagValueEnter(self,event):
        '''enter the tag value'''
        self.Value = self.textCtrl_tag_value.GetValue().strip()
        
    def getTagElement(self):
        '''return the tag element'''
        if self.tag_id_is_valid:
            return {"ID":self.ID, "VR":self.VR, "Value":self.Value}
        return None

class CustomizedTagPanel(wx.Panel):
    '''provide the panel to customized tag'''
    def __init__(self,parent,id=-1):
        wx.Panel.__init__(self,parent,id)        
        self.SetSize(parent.GetSize())
        self.module_name = ''
        self.function_name = ''
        self.function_name_list = []
        self.tag_is_valid = False
        self.GUI_init()
        
    def GUI_init(self):
        # font for static text
        font_st = getControlFont('st')
        # font for button lable
        font_btn = getControlFont('btn')
        
        # 自定义转换文件路径
        st_file_path = wx.StaticText(self,-1,u'DICOM自定义转换文件路径:',style=wx.TE_CENTER)
        st_file_path.SetFont(font_st)
        st_file_path.SetBackgroundColour("White")
        st_file_path.SetForegroundColour('Black')
                
        size = wx.Size(self.ClientSize.x/2,10)      
        self.textCtrl_file_path = wx.TextCtrl(self,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
        self.Bind(wx.EVT_TEXT,self.OnFilePathEnter,self.textCtrl_file_path)
                
        browseBtn_file = wx.Button(self,-1,label=u'浏览...',size=(100,30))
        browseBtn_file.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnFileBrowser,browseBtn_file) 
        
        # 显示文件关联的模块名
        self.st_module_name = wx.StaticText(self,-1,u'模块名:',style=wx.TE_CENTER)
        self.st_module_name.SetFont(font_st)
        self.st_module_name.SetBackgroundColour("White")
        self.st_module_name.SetForegroundColour('Black')
        self.st_module_name.Show(False)

        self.st_module_name_display = wx.StaticText(self,-1,u'',style=wx.TE_CENTER)
        self.st_module_name_display.SetFont(font_st)
        self.st_module_name_display.SetBackgroundColour("White")
        self.st_module_name_display.SetForegroundColour('Black')
        self.st_module_name_display.Show(False)
        
        # 显示文件关联的函数名
        self.st_function_name = wx.StaticText(self,-1,u'函数名:',style=wx.TE_CENTER)
        self.st_function_name.SetFont(font_st)
        self.st_function_name.SetBackgroundColour("White")
        self.st_function_name.SetForegroundColour('Black')
        self.st_function_name.Show(False)
        
        self.comboBoxFuncName = wx.ComboBox(self,-1,choices=self.function_name_list,style=wx.CB_SORT|wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnComboxFuncNmaeClick,self.comboBoxFuncName)        
        self.comboBoxFuncName.Show(False)
                
        self.flexSizer = wx.FlexGridSizer(cols=3,hgap=10,vgap=10)       
        self.flexSizer.Add(st_file_path,0,wx.ALIGN_CENTER)
        self.flexSizer.Add(self.textCtrl_file_path,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer.Add(browseBtn_file,0,wx.ALIGN_TOP)
        self.flexSizer.Add(self.st_module_name,0,wx.ALIGN_CENTER)
        self.flexSizer.Add(self.st_module_name_display,0,wx.ALIGN_CENTER)
        self.flexSizer.AddSpacer(20)
        self.flexSizer.Add(self.st_function_name,0,wx.ALIGN_CENTER)
        self.flexSizer.Add(self.comboBoxFuncName,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer.AddSpacer(20)
        self.SetSizer(self.flexSizer)
        self.flexSizer.Fit(self)
        self.Center()
        
    def Refresh(self):
        self.flexSizer.Fit(self)
        self.flexSizer.Layout()
        
    def OnComboxFuncNmaeClick(self,event):
        '''select the function name from the drop list'''
        self.function_name = self.comboBoxFuncName.GetValue().strip()
    
    def _validate(self,filename):
        '''check if the customized transform file is valid or not'''
        # check if the file existed
        if not os.path.exists(filename):
            message = u"文件:%s 不存在!" %filename
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        # check if the file extension is *.xls or *.xlsx
        extension = filename.split('.')[-1].strip()
        if extension != 'py' and extension != 'pyw':
            message = u"文件扩展名应该是.py或.pyw，实际扩展名为.%s!" %extension
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        return True  
    
    def _Show(self,bShow):
        '''show or hide.
        [param][in] bShow:True to show,else hide
        '''  
        self.st_module_name.Show(bShow)
        self.st_module_name_display.Show(bShow)
        self.st_function_name.Show(bShow)
        self.comboBoxFuncName.Show(bShow)                
        if bShow:
            # set the display module name
            baseName = os.path.basename(self.file_custom_path)
            module_path = os.path.dirname(self.file_custom_path)
            if module_path not in sys.path:
                sys.path.append(module_path)
            pos = baseName.find('.')
            self.module_name = baseName[:pos]
            self.st_module_name_display.SetLabel(self.module_name)
            lsFuncName = self.getFuncNameList(self.file_custom_path)
            # first clear
            self.comboBoxFuncName.Clear() 
            self.comboBoxFuncName.AppendItems(lsFuncName)           
        # refresh the GUI
        self.Refresh()
        
    def getTagElement(self):
        if self.tag_is_valid and len(self.function_name) > 0:
            return {"ModuleName":self.module_name,"FunctionName":self.function_name}
        return None     
            
    def getFuncNameList(self,filename):
        '''get the function list defined at the file.
        [param][in] filename:file to parse
        '''
        fread = open(filename,'r')
        lsFuncName = []
        for line in fread.readlines():
            if line.startswith('def '):
                line = line.strip('def ').strip()
                pos = line.find('(')
                funcName = line[:pos].strip()
                lsFuncName.append(funcName)
        return lsFuncName
    
    def OnFileBrowser(self,event):
        filename_custom = wx.FileSelector(u'选择一个自定义转换文件',default_path='',\
            default_extension='*.py',wildcard="Python files(*.py)|*.py|Python files(*.pyw)|*.pyw|All files(*.*)|*.*",parent=self)  
        
        if len(filename_custom) > 0:
            self.textCtrl_file_path.Clear()
            self.textCtrl_file_path.AppendText(filename_custom.strip())
            
        
    def OnFilePathEnter(self,event):
        self.file_custom_path = self.textCtrl_file_path.GetValue().strip()
        if len(self.file_custom_path) > 0:
            if self._validate(self.file_custom_path) == False:
                self.textCtrl_file_path.Clear()
                self._Show(False)
                self.tag_is_valid = False
            else:
                self._Show(True)
                self.tag_is_valid = True
    
class DeleteTagPanel(wx.Panel):
    '''provide the panel to delete one tag'''
    def __init__(self,parent,id=-1,tag_id_list=None):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,20))
        self.ID = ''
        self.tag_id_list = tag_id_list
        self.GUI_init()
    
    def GUI_init(self):
        font_st = getControlFont('st')       
                
        # tag id
        st_tag_id = wx.StaticText(self,-1,u'Tag ID:',style=wx.TE_CENTER)
        st_tag_id.SetFont(font_st)
        st_tag_id.SetBackgroundColour("White")
        st_tag_id.SetForegroundColour('Black')
        
        self.tag_id_control = wx.ComboBox(self,-1,choices=self.tag_id_list,style=wx.CB_READONLY|wx.CB_SORT)
        self.Bind(wx.EVT_COMBOBOX,self.OnTagIDEnter,self.tag_id_control)
        
        box_sizer_h = wx.BoxSizer(wx.HORIZONTAL) 
        box_sizer_h.Add(st_tag_id,0,wx.ALIGN_CENTER) 
        box_sizer_h.AddSpacer(10)                 
        box_sizer_h.Add(self.tag_id_control,0,wx.ALIGN_TOP|wx.EXPAND)
        
        self.SetSizer(box_sizer_h)
        box_sizer_h.Fit(self)
        self.Center()
        
    def OnTagIDEnter(self,event):
        '''check if the tag id is in such form:0x00080070'''
        id = self.tag_id_control.GetValue().strip().lower()        
        # transform from (xxxx,xxxx) to '0xxxxxxxxx'
        ls_id = id.split(', ')            
        id = '0x' + ls_id[0][1:] + ls_id[1][:-1]            
        if not id.startswith('0x'):
            message = u"Tag ID:%s 应以0x开头!" %id
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            self.tag_id_control.Clear()
            self.tag_id_is_valid = False            
        else:
            tag_id = id[2:]
            if len(tag_id) != 8:
                message = u"Tag ID:%s 在0x之后应有8位!" %id
                wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                self.tag_id_control.Clear()
                self.tag_id_is_valid = False  
            else:
                try:
                    int(tag_id,16)
                    self.ID = id
                    self.tag_id_is_valid = True  
                except ValueError:
                    message = u"Tag ID:%s 不是有效的16进制!" %id
                    wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                    self.tag_id_control.Clear()
                    self.tag_id_is_valid = False        

    def getTagIDToDelete(self):
        return self.ID
    
    def getTagElement(self):
        return {"ID":self.ID}    
        
        
class AddModifyTagByReferenceTagPanel(wx.Panel):
    '''provide the panel to add or modify one tag by reference tag'''
    def __init__(self,parent,id=-1,op='+',tag_id_list=None):
        wx.Panel.__init__(self,parent,id)
        self.SetSize((parent.ClientSize.x,20))
        self.op = op
        self.ID = ''
        self.VR = ''
        self.ReferenceTagID = ''
        self.ReferenceTagVR = ''
        self.tag_id_is_valid = False
        self.tag_id_list = tag_id_list
        self.DICOM_VR = ["AE", "AS", "AT", "CS", 
        "DA", "DS", "DT", "FL", 
        "FD", "IS", "LO", "LT", 
        "OB", "OF", "OW", "PN",
        "SH", "SL", "SQ", "SS",
        "ST", "TM", "UI", "UL",
        "UN", "US", "UT"]

        self.GUI_init()
        
    def GUI_init(self):
        font_st = getControlFont('st')       
        
        # tag id
        st_tag_id = wx.StaticText(self,-1,u'ID:',style=wx.TE_CENTER)
        st_tag_id.SetFont(font_st)
        st_tag_id.SetBackgroundColour("White")
        st_tag_id.SetForegroundColour('Black')       
        
        
        size = wx.Size(self.ClientSize.x/4,20)
        
        # if op = add,then just input tag id
        # if op = modify,then allow to select from droplist
        if self.op == '+':
            self.tag_id_control = wx.TextCtrl(self,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
            self.Bind(wx.EVT_TEXT_ENTER,self.OnTagIDEnter,self.tag_id_control)
        else:
            self.tag_id_control = wx.ComboBox(self,-1,choices=self.tag_id_list,style=wx.CB_READONLY|wx.CB_SORT)
            self.Bind(wx.EVT_COMBOBOX,self.OnTagIDEnter,self.tag_id_control)           

        # tag vr,current version with no verification between vr and value
        st_tag_vr = wx.StaticText(self,-1,u'VR:',style=wx.TE_CENTER)
        st_tag_vr.SetFont(font_st)
        st_tag_vr.SetBackgroundColour("White")
        st_tag_vr.SetForegroundColour('Black')
        
        self.comboBoxVR = wx.ComboBox(self,-1,choices=self.DICOM_VR,style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnComboxVRClick,self.comboBoxVR)
        
        # ReferenceTagID
        st_tag_id_ref = wx.StaticText(self,-1,u'Reference ID:',style=wx.TE_CENTER)
        st_tag_id_ref.SetFont(font_st)
        st_tag_id_ref.SetBackgroundColour("White")
        st_tag_id_ref.SetForegroundColour('Black')
        
        self.comboBoxTagIDRef = wx.ComboBox(self,-1,choices=self.tag_id_list,style=wx.CB_READONLY|wx.CB_SORT)
        self.Bind(wx.EVT_COMBOBOX,self.OnRefTagIDEnter,self.comboBoxTagIDRef)  
        
        # ReferenceTagVR
        st_tag_vr_ref = wx.StaticText(self,-1,u'Reference VR:',style=wx.TE_CENTER)
        st_tag_vr_ref.SetFont(font_st)
        st_tag_vr_ref.SetBackgroundColour("White")
        st_tag_vr_ref.SetForegroundColour('Black')
        
        self.comboBoxVRRef = wx.ComboBox(self,-1,choices=self.DICOM_VR,style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX,self.OnComboxVRRefClick,self.comboBoxVRRef)              
        
        box_sizer_h = wx.BoxSizer(wx.HORIZONTAL) 
        box_sizer_h.Add(st_tag_id,0,wx.ALIGN_CENTER) 
        box_sizer_h.AddSpacer(10)                 
        box_sizer_h.Add(self.tag_id_control,0,wx.ALIGN_TOP|wx.EXPAND) 
        box_sizer_h.AddSpacer(10)        
        box_sizer_h.Add(st_tag_vr,0,wx.ALIGN_CENTER)
        box_sizer_h.AddSpacer(10)                     
        box_sizer_h.Add(self.comboBoxVR,0,wx.ALIGN_TOP) 
        box_sizer_h.AddSpacer(10)      
        box_sizer_h.Add(st_tag_id_ref,0,wx.ALIGN_CENTER) 
        box_sizer_h.AddSpacer(10)      
        box_sizer_h.Add(self.comboBoxTagIDRef,0,wx.ALIGN_TOP)
        box_sizer_h.AddSpacer(10)                         
        box_sizer_h.Add(st_tag_vr_ref,0,wx.ALIGN_CENTER)  
        box_sizer_h.AddSpacer(10)                    
        box_sizer_h.Add(self.comboBoxVRRef,0,wx.ALIGN_TOP)
        self.SetSizer(box_sizer_h)
        box_sizer_h.Fit(self)
        self.Center()        

    def OnTagIDEnter(self,event):
        '''check if the tag id is in such form:0x00080070'''
        id = self.tag_id_control.GetValue().strip().lower()        
        # transform from (xxxx,xxxx) to '0xxxxxxxxx'
        if self.op != '+':
            ls_id = id.split(', ')            
            id = '0x' + ls_id[0][1:] + ls_id[1][:-1]            
        if not id.startswith('0x'):
            message = u"Tag ID:%s 应以0x开头!" %id
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            self.tag_id_control.Clear()
            self.tag_id_is_valid = False            
        else:
            tag_id = id[2:]
            if len(tag_id) != 8:
                message = u"Tag ID:%s 在0x之后应有8位!" %id
                wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                self.tag_id_control.Clear()
                self.tag_id_is_valid = False  
            else:
                try:
                    int(tag_id,16)
                    self.ID = id
                    self.tag_id_is_valid = True  
                except ValueError:
                    message = u"Tag ID:%s 不是有效的16进制!" %id
                    wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
                    self.tag_id_control.Clear()
                    self.tag_id_is_valid = False    
        
    
    
    def OnComboxVRClick(self,event):
        '''select the VR type from the drop list'''
        self.VR = self.comboBoxVR.GetValue().strip()
    
    def OnRefTagIDEnter(self,event):
        '''enter the reference tag id value'''
        reference_id = self.comboBoxTagIDRef.GetValue().strip()
        ls_id = reference_id.split(', ')            
        self.ReferenceTagID = '0x' + ls_id[0][1:] + ls_id[1][:-1]         
        

    def OnComboxVRRefClick(self,event):
        '''select the VR type of reference tag from drop list'''
        self.ReferenceTagVR = self.comboBoxVRRef.GetValue().strip()
        
    def getTagElement(self):
        '''return the tag element in dict form'''
        if self.tag_id_is_valid:            
            return {"ID":self.ID, "VR":self.VR, "ReferenceTagID":self.ReferenceTagID, "ReferenceTagVR":self.ReferenceTagVR}
        return None

            
        
        
        
        
        

class SeriesDicomConverterGUIPanel(wx.Panel):
    '''define a panel to set the dicom convert rules by GUI'''
    def __init__(self,parent,dicom_file_name,id=-1):
        wx.Panel.__init__(self,parent,id)             
        self.dicom_file_name = dicom_file_name        
        self.GUI_init()
        
    def GUI_init(self):
        font_st = getControlFont('st')
        font_btn = getControlFont('btn')  
        
        
        # Add Tag List         
        dfile = dicom.read_file(self.dicom_file_name)
        keys = dfile.keys()
        tag_ids = [str(key) for key in keys]            
       
        # add tag
        self.panel_add_tag = wx.Panel(self,-1)
        self.addTagCheckBox = wx.CheckBox(self.panel_add_tag,-1,label=u'添加tag',size=(120,30))
        self.addTagCheckBox.SetFont(font_st)
        self.Bind(wx.EVT_CHECKBOX,self.OnAddTagChecked,self.addTagCheckBox)
        
        self.add_panel = AddModifyDeleteTagPanel(self.panel_add_tag,-1,'+',tag_ids)
        
        self.box_sizer_v_add = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v_add.Add(self.addTagCheckBox,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.box_sizer_v_add.Add(self.add_panel,0,wx.ALL|wx.ALIGN_BOTTOM|wx.EXPAND,border=10)
        self.box_sizer_v_add.Hide(self.add_panel)
        
        self.panel_add_tag.SetSizer(self.box_sizer_v_add)       
        self.box_sizer_v_add.Fit(self.panel_add_tag)
        self.panel_add_tag.Center() 
        
        # delete tag
        self.panel_del_tag = wx.Panel(self,-1)
        self.delTagCheckBox = wx.CheckBox(self.panel_del_tag,-1,label=u'删除tag',size=(120,30))
        self.delTagCheckBox.SetFont(font_st)
        self.Bind(wx.EVT_CHECKBOX,self.OnDelTagChecked,self.delTagCheckBox)
                       
        self.del_panel = AddModifyDeleteTagPanel(self.panel_del_tag,-1,'-',tag_ids)
                       
        self.box_sizer_v_del = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v_del.Add(self.delTagCheckBox,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.box_sizer_v_del.Add(self.del_panel,0,wx.ALL|wx.ALIGN_BOTTOM,border=10)
        self.box_sizer_v_del.Hide(self.del_panel)
                       
        self.panel_del_tag.SetSizer(self.box_sizer_v_del)       
        self.box_sizer_v_del.Fit(self.panel_del_tag)
        self.panel_del_tag.Center()
        
        # modify tag
        self.panel_mod_tag = wx.Panel(self,-1)
        self.modTagCheckBox = wx.CheckBox(self.panel_mod_tag,-1,label=u'修改tag',size=(120,30))
        self.modTagCheckBox.SetFont(font_st)
        self.Bind(wx.EVT_CHECKBOX,self.OnModTagChecked,self.modTagCheckBox)
                
        self.mod_panel = AddModifyDeleteTagPanel(self.panel_mod_tag,-1,'m',tag_ids)
                
        self.box_sizer_v_mod = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v_mod.Add(self.modTagCheckBox,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.box_sizer_v_mod.Add(self.mod_panel,0,wx.ALL|wx.ALIGN_BOTTOM|wx.EXPAND,border=10)
        self.box_sizer_v_mod.Hide(self.mod_panel)
                
        self.panel_mod_tag.SetSizer(self.box_sizer_v_mod)       
        self.box_sizer_v_mod.Fit(self.panel_mod_tag)
        self.panel_mod_tag.Center() 
        
        # cutomize tag
        self.panel_cus_tag = wx.Panel(self,-1)
        self.panel_cus_tag.SetSize((400,120))
        self.cusTagCheckBox = wx.CheckBox(self.panel_cus_tag,-1,label=u'自定义',size=(120,30))
        self.cusTagCheckBox.SetFont(font_st)
        self.Bind(wx.EVT_CHECKBOX,self.OnCusTagChecked,self.cusTagCheckBox)       
        self.cus_panel = CustomizedTagPanel(self.panel_cus_tag,-1)
                               
        self.box_sizer_v_cus = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v_cus.Add(self.cusTagCheckBox,0,wx.ALL|wx.ALIGN_TOP,border=10)
        self.box_sizer_v_cus.Add(self.cus_panel,0,wx.ALL|wx.ALIGN_BOTTOM|wx.EXPAND,border=10)
        self.box_sizer_v_cus.Hide(self.cus_panel)
                               
        self.panel_cus_tag.SetSizer(self.box_sizer_v_cus)       
        self.box_sizer_v_cus.Fit(self.panel_cus_tag)
        self.panel_cus_tag.Center()
        
        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v.Add(self.panel_add_tag,0,wx.ALL|wx.EXPAND)        
        self.box_sizer_v.Add(self.panel_del_tag,0,wx.ALL|wx.EXPAND)        
        self.box_sizer_v.Add(self.panel_mod_tag,0,wx.ALL|wx.EXPAND)        
        self.box_sizer_v.Add(self.panel_cus_tag,0,wx.ALL|wx.EXPAND)       
        
        
        self.SetSizer(self.box_sizer_v)
        self.box_sizer_v.Fit(self)
        self.Center() 
    
    def getAddTagElements(self):
        return self.add_panel.getTagElements()
    
    def getDelTagElements(self):
        return self.del_panel.getTagElements()
    
    def getModTagElements(self):
        return self.mod_panel.getTagElements()
    
    def getCusTagElements(self):
        lsTags = []
        tag = self.cus_panel.getTagElement()
        if tag is not None:
            lsTags.append(tag)
        return lsTags
    
    
    def Refresh(self):
        '''refresh all the panels''' 
        self.add_panel.Refresh()       
        self.box_sizer_v_add.Fit(self.panel_add_tag)
        self.box_sizer_v_add.Layout()
        self.panel_add_tag.Center()
        self.del_panel.Refresh()
        self.box_sizer_v_del.Fit(self.panel_del_tag)
        self.box_sizer_v_del.Layout()
        self.panel_del_tag.Center()
        self.mod_panel.Refresh()
        self.box_sizer_v_mod.Fit(self.panel_mod_tag)
        self.box_sizer_v_mod.Layout()
        self.panel_mod_tag.Center()
        self.cus_panel.Refresh()
        self.box_sizer_v_cus.Fit(self.panel_cus_tag)
        self.box_sizer_v_cus.Layout()
        self.panel_cus_tag.Center()       
        
        self.box_sizer_v.Fit(self)
        self.box_sizer_v.Layout()        
        self.Center()      
        
    
    def OnAddTagChecked(self,event):
        '''add tag check box is checked or not'''
        if self.addTagCheckBox.IsChecked():
            self.box_sizer_v_add.Show(self.add_panel)          

        else:
            self.box_sizer_v_add.Hide(self.add_panel)
        self.Refresh()
        
        
    def OnDelTagChecked(self,event):
        '''delete tag check box is checked or not'''
        if self.delTagCheckBox.IsChecked():
            self.box_sizer_v_del.Show(self.del_panel)
        else:
            self.box_sizer_v_del.Hide(self.del_panel)
        self.Refresh()
            
               
    def OnModTagChecked(self,event):
        '''modify tag check box is checked or not'''
        if self.modTagCheckBox.IsChecked():
            self.box_sizer_v_mod.Show(self.mod_panel)
        else:
            self.box_sizer_v_mod.Hide(self.mod_panel)
        self.Refresh()
            
    def OnCusTagChecked(self,event):
        '''customize tag check box is checked or not'''
        if self.cusTagCheckBox.IsChecked():
            self.box_sizer_v_cus.Show(self.cus_panel)
        else:
            self.box_sizer_v_cus.Hide(self.cus_panel)
        self.Refresh()
        
            
        
class DicomDataPathSelFrame(wx.Frame):
    """The frame provide GUI to select the dicom series and files to convert.       
    """
    def __init__(self,parent,id):
        wx.Frame.__init__(self,parent,id,u'DICOM转换序列选择对话框',size=(1200,400),style=wx.CAPTION|wx.BORDER_RAISED)
        self.src_data_path = ""
        self.dst_data_path = ""
        self.src_data_path_check_passed = False
        self.dst_data_path_check_passed = False       
        self.series_selected = []
        self.series = []
        self.file_in_memory = r'D:\DICOMDataConverter\convert_files.txt'
        self.series_selected_path = []
        self.series_path_src = []
        self.checked_series_index = None        
        self.GUIInit()
        
    def GUIInit(self):        
        # font 
        font_st = getControlFont('st')
        font_btn = getControlFont('btn')
        lsNames = []
        try:
            rfile = open(self.file_in_memory,'r')
            lsNames = rfile.readlines()
        except IOError:
            pass
        
        
        self.panel_path = wx.Panel(self,-1)        
        st_src_path = wx.StaticText(self.panel_path,-1,u'源文件路径:',style=wx.TE_CENTER)
        st_src_path.SetFont(font_st)
        st_src_path.SetBackgroundColour("White")
        st_src_path.SetForegroundColour('Black')
        size = wx.Size(self.ClientSize.x/2,30)
        self.textCtrl_src = wx.TextCtrl(self.panel_path,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
        self.Bind(wx.EVT_TEXT,self.OnSrcTextEnter,self.textCtrl_src)     
        
        
        browseBtn_src = wx.Button(self.panel_path,-1,label=u'浏览...',size=(100,30))
        browseBtn_src.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnSrcFileBrowser,browseBtn_src)  
        
       
        st_dst_path = wx.StaticText(self.panel_path,-1,u'结果文件路径:',style=wx.TE_CENTER)
        st_dst_path.SetFont(font_st)
        st_dst_path.SetBackgroundColour("White")
        st_dst_path.SetForegroundColour('Black')
        
        self.textCtrl_dst = wx.TextCtrl(self.panel_path,-1,style=wx.TE_LEFT|wx.TE_PROCESS_ENTER,size=size)
        self.Bind(wx.EVT_TEXT,self.OnDstTextEnter,self.textCtrl_dst)
        browseBtn_dst = wx.Button(self.panel_path,-1,label=u'浏览...',size=(100,30))
        browseBtn_dst.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnDstFileBrowser,browseBtn_dst)
        
        st_series = wx.StaticText(self.panel_path,-1,u'序列选择:',style=wx.TE_CENTER)
        st_series.SetFont(font_st)
        st_series.SetBackgroundColour("White")
        st_series.SetForegroundColour('Black')
        
        self.checklistBox = wx.CheckListBox(self.panel_path,-1,choices=[])
        self.Bind(wx.EVT_CHECKLISTBOX,self.OnCheckClicked,self.checklistBox)            

        self.flexSizer_path = wx.FlexGridSizer(cols=3,hgap=10,vgap=40)       
        self.flexSizer_path.Add(st_src_path,0,wx.ALIGN_CENTER)
        self.flexSizer_path.Add(self.textCtrl_src,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer_path.Add(browseBtn_src,0,wx.ALIGN_TOP)
        self.flexSizer_path.Add(st_dst_path,0,wx.ALIGN_CENTER)
        self.flexSizer_path.Add(self.textCtrl_dst,0,wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer_path.Add(browseBtn_dst,0,wx.ALIGN_TOP)
        self.flexSizer_path.Add(st_series,0,wx.ALIGN_CENTER)
        self.flexSizer_path.Add(self.checklistBox,1,wx.ALL|wx.ALIGN_TOP|wx.EXPAND)
        self.flexSizer_path.AddGrowableCol(1,100)
        
        
        self.panel_path.SetSizer(self.flexSizer_path)
        self.flexSizer_path.Fit(self.panel_path)
        self.panel_path.Center()        

        panel_btn = wx.Panel(self,-1)
        self.okBtn = wx.Button(panel_btn,-1,label=u'确定',size=(100,30))
        self.okBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnOK,self.okBtn)
        self.okBtn.Enable(False)
        self.cancelBtn = wx.Button(panel_btn,-1,label=u'取消',size=(100,30))
        self.cancelBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.cancelBtn)
        self.exitBtn = wx.Button(panel_btn,-1,label=u'退出',size=(100,30))
        self.exitBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnExit,self.exitBtn)
        
        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.okBtn,0,wx.ALL|wx.ALIGN_TOP,border=10)
        box_sizer.AddStretchSpacer()
        box_sizer.Add(self.cancelBtn,0,wx.ALL|wx.ALIGN_TOP,border=10)
        box_sizer.AddStretchSpacer()
        box_sizer.Add(self.exitBtn,0,wx.ALL|wx.ALIGN_TOP,border=10)
        panel_btn.SetSizer(box_sizer)
        box_sizer.Fit(panel_btn)
        panel_btn.Center() 
        
        if len(lsNames) == 2:
            self.textCtrl_src.AppendText(lsNames[0])
            self.textCtrl_dst.AppendText(lsNames[1])         
        

        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v.Add(self.panel_path,1,wx.ALL|wx.EXPAND,10)       
        self.box_sizer_v.Add(panel_btn,1,wx.ALL|wx.EXPAND,10)
        self.SetSizer(self.box_sizer_v)
        self.box_sizer_v.Fit(self)
        self.Center()    

    def OnExit(self,event):
        self.Destroy()

    def OnSrcFileBrowser(self,event):        
        dialog = wx.DirDialog(self,u'选择要转换的DICOM文件路径',style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:            
            self.textCtrl_src.Clear()
            self.textCtrl_src.AppendText(dialog.GetPath())
        dialog.Destroy()
        
    def OnDstFileBrowser(self,event):        
        dialog = wx.DirDialog(self,u'选择保存转换后的DICOM文件路径',style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:            
            self.textCtrl_dst.Clear()
            self.textCtrl_dst.AppendText(dialog.GetPath())
        dialog.Destroy()       


    def OnSrcTextEnter(self,event):
        src_data_path = self.textCtrl_src.GetValue().strip() 
        if len(src_data_path) == 0:
            self.src_data_path_check_passed = False
        elif self.pathValidCheck(src_data_path,True) == False:
            self.textCtrl_src.Clear()
            self.textCtrl_src.SetFocus()
            self.src_data_path_check_passed = False
            self.okBtn.Enable(False)
        else:
            self.src_data_path_check_passed = True
            self.src_data_path = src_data_path
        self.AddCheckBoxListItems()
  

    def OnDstTextEnter(self,event):
        dst_data_path = self.textCtrl_dst.GetValue().strip()
        if len(dst_data_path) == 0:
            self.dst_data_path_check_passed = False
        elif self.pathValidCheck(dst_data_path,False) == False:           
            self.textCtrl_dst.Clear()
            self.textCtrl_dst.SetFocus()
            self.dst_data_path_check_passed = False
            self.okBtn.Enable(False)
        else:
            self.dst_data_path_check_passed = True
            self.dst_data_path = dst_data_path
        self.AddCheckBoxListItems()
    
    def hasSeriesData(self,pathname):
        '''check if there is any dicom file under the path'''
        index = 0
        for root,dirs,names in os.walk(pathname):
            if len(names) > 0:
                index += 1
                dfilename = glob.glob(root + os.sep + "*.dcm")[0]
                dfile = dicom.read_file(dfilename)
                series_id = dfile.SeriesInstanceUID
                self.series.append(series_id)
                self.series_path_src.append(root)
        if index > 0:
            return True
        return False
        
        
    def pathValidCheck(self,pathname,checkFiles):
        # check if the path existed
        if not os.path.exists(pathname):
            message = u"路径:%s 不存在!" %pathname
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        # check if the path contains series data
        if checkFiles and self.hasSeriesData(pathname) == False:
            message = u"路径:%s下没有DICOM文件!" %pathname
            wx.MessageBox(message,u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return False
        return True      
        

    def AddCheckBoxListItems(self):
        # only add after the path valid check passed
        self.checklistBox.Clear()
        if self.src_data_path_check_passed and self.dst_data_path_check_passed:
            # add series id from series list
            lsSeries = []
            index = 1
            for id in self.series:
                series_id = u"序列%d:%s" %(index,id)
                index += 1
                lsSeries.append(series_id)                    
            self.checklistBox.AppendItems(lsSeries)                           
    

    def OnCheckClicked(self,event):
        # get the turple of item index checked from the series list
        self.checked_series_index = self.checklistBox.GetChecked()        
        if len(self.checked_series_index) == 0: # no series selected
            self.okBtn.Enable(False)
        else:
            self.okBtn.Enable(True)     
    
    
    def OnOK(self,event):
        # check if the source data path is the same as the destination data path
        if self.src_data_path == self.dst_data_path:
            wx.MessageBox(u'source data path should not be the same as destination data path!',u"友情提示",wx.OK|wx.ICON_EXCLAMATION)
            return
        # remove the possible readonly attribute of destination file path
        command = 'attrib -r %s' % self.dst_data_path
        os.popen(command)        
        
        # get the series checked list
        self.series_selected = []       
        for i in self.checked_series_index:
            self.series_selected.append(self.series[i])
            self.series_selected_path.append(self.series_path_src[i])
        
        # save the file name selected into a text file
        wfile = open(self.file_in_memory,'w')
        wfile.writelines([self.src_data_path+'\n',self.dst_data_path+'\n'])
        wfile.close()
        
        
        # Close this GUI and Open the TestFrame GUI
        self.Hide()
        frame = SeriesDicomConverterFrame(None,self.checked_series_index,self.series_selected,self.series_selected_path,self.dst_data_path)
        frame.Show()
        self.Destroy()
    
    def OnCancel(self,event):
        # undo the selection or input for the file and sheets
        self.textCtrl_src.Clear()
        self.textCtrl_dst.Clear()
        self.checklistBox.Clear()
        self.okBtn.Enable(False)



class SeriesDicomConverterFrame(wx.Frame,GenericDispatchMix):
    '''the frame provides the GUI for each series dicom convert operation'''
    def __init__(self,parent,series_index_list,series_id_list,series_path_list,dst_data_path,id=-1):
        wx.Frame.__init__(self,parent,id,u'序列DICOM转换对话框',size=(800,1200),style=wx.CAPTION|wx.BORDER_RAISED)
        GenericDispatchMix.__init__(self)       
        self.series_index_list = series_index_list
        self.series_id_list = series_id_list
        self.series_path_list = series_path_list
        self.series_convert_paras = []
        self.dst_data_path = dst_data_path              
        self.GUI_init()
    
    
        
    def getImagePath(self,dicom_file_path,suffix):
        '''get the full path of the first dicom file under the specific path with
           the specific suffix.
        [param][in] dicom_file_path:the dicom directory path 
        [param][in] suffix:the suffix of the dicom files to search
        '''        
        lsDicom = glob.glob(dicom_file_path + os.sep + suffix)
        return lsDicom[0]
    
    def GUI_init(self):
        font_btn = getControlFont('btn')
        # create the dicom convert panel
        dicom_file_name = self.getImagePath(self.series_path_list[0],"*.dcm")
        # bind an event handler which indicates the current series convert is defined
        self.Bind(EVT_DICOM_CONVERT_DEFINE,self.OnSeriesConvertDefine)  
        size = (self.ClientSize.x,self.ClientSize.y-200)        
        self.panel_series_convert = SeriesDicomConverterPanel(self,size,self.dst_data_path,dicom_file_name,-1,self.series_index_list[0]+1,self.series_index_list)
        self.panel_series_convert.Show()
        
        panel_2 = wx.Panel(self,-1)       
        self.okBtn = wx.Button(panel_2,-1,label=u'确定',size=(100,30))
        self.okBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnOK,self.okBtn)
        self.okBtn.Enable(False)
        
        self.cancelBtn = wx.Button(panel_2,-1,label=u'取消',size=(100,30))
        self.cancelBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.cancelBtn)
        
        self.exitBtn = wx.Button(panel_2,-1,label=u'退出',size=(100,30))
        self.exitBtn.SetFont(font_btn)
        self.Bind(wx.EVT_BUTTON,self.OnExit,self.exitBtn)
                
        box_sizer_h_2 = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer_h_2.AddStretchSpacer()     
        box_sizer_h_2.Add(self.okBtn,0,wx.ALL|wx.ALIGN_TOP)
        box_sizer_h_2.AddSpacer(30)
        box_sizer_h_2.Add(self.cancelBtn,0,wx.ALL|wx.ALIGN_TOP)
        box_sizer_h_2.AddSpacer(30)
        box_sizer_h_2.Add(self.exitBtn)
                        
        panel_2.SetSizer(box_sizer_h_2)
        box_sizer_h_2.Fit(panel_2)
        panel_2.Center()
        
        
        self.box_sizer_v = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer_v.SetMinSize((800,1000))
        self.box_sizer_v.Add(self.panel_series_convert,1,wx.ALL|wx.EXPAND)
        self.box_sizer_v.AddSpacer(20)
        self.box_sizer_v.Add(panel_2,0,wx.ALIGN_BOTTOM|wx.EXPAND)
        self.SetSizer(self.box_sizer_v)
        self.box_sizer_v.Fit(self)
        self.Center()
    
    def OnSeriesConvertDefine(self,event):
        '''event handler for series dicom convert rule is defined.'''
        values = event.getTurpleValue()
        filename = values[0]
        index = values[1] 
        bApply = values[2]
        bComplete = values[3]
              
        list_index = self.series_index_list.index(index)
        series_file_path = self.series_path_list[list_index]
        paras = (series_file_path,self.dst_data_path,filename)
        
        self.series_convert_paras.append(paras)        
        
        if not bComplete:
            if bApply:
                # apply for left series
                for series_path in self.series_path_list[list_index+1:]:
                    paras = (series_path,self.dst_data_path,filename)
                    self.series_convert_paras.append(paras)
                # enable OK button to start convert
                self.box_sizer_v.Remove(self.panel_series_convert)
                self.panel_series_convert.Hide()
                self.box_sizer_v.SetMinSize((400,40))
                self.box_sizer_v.Fit(self)
                self.box_sizer_v.Layout()
                self.Center()            
                self.okBtn.Enable()
            else:
                # load a convert setting panel for next series
                self.box_sizer_v.Remove(self.panel_series_convert)
                self.panel_series_convert.Hide()
                size = (self.ClientSize.x,self.ClientSize.y-200)
                dicom_file_name = self.getImagePath(self.series_path_list[list_index+1],"*.dcm")        
                self.panel_series_convert = SeriesDicomConverterPanel(self,size,self.dst_data_path,dicom_file_name,-1,self.series_index_list[list_index+1]+1,self.series_index_list)
                self.box_sizer_v.Insert(0,self.panel_series_convert,1,wx.ALL|wx.EXPAND)
                self.box_sizer_v.Fit(self)
                self.box_sizer_v.Layout()
                self.Center()
        else:
            self.box_sizer_v.Remove(self.panel_series_convert)
            self.panel_series_convert.Hide()
            self.box_sizer_v.SetMinSize((400,40))
            self.box_sizer_v.Fit(self)
            self.box_sizer_v.Layout()
            self.Center()            
            self.okBtn.Enable()
    
    def adjust(self):
        '''adjust the number of series to convert to account for some possible canceled series
        '''
        index = 0
        ls_series_index = list(self.series_index_list)
        for para in self.series_convert_paras:
            fileName = para[2]
            if fileName is None:
                index = self.series_convert_paras.index(para)
                self.series_convert_paras.pop(index)
                self.series_id_list.pop(index)
                ls_series_index.pop(index)
        self.series_index_list = tuple(ls_series_index)
        
        
    def OnOK(self,event):
        '''begin to convert all selected series'''
        size = (600,400)
        self.box_sizer_v.SetMinSize(size)
        self.adjust()
        panel_progress = SeriesDicomConvertProgressPanel(self,size,self.series_convert_paras,self.series_id_list,self.series_index_list)
        
        self.box_sizer_v.Insert(0,panel_progress,1,wx.ALL|wx.EXPAND)
        self.box_sizer_v.Fit(self)
        self.box_sizer_v.Layout()
        self.Center()
        panel_progress.run()
        self.okBtn.Enable(False)
    
    def OnCancel(self,event):
        # prompt if to cancel the convert
        if wx.MessageBox(u"是否取消转换?","Yes Or No...",style=wx.YES|wx.NO|wx.ICON_QUESTION) == wx.YES:
            self.Destroy()
        
        
    
    def OnExit(self,event):
        self.Destroy()
        

if __name__ == '__main__':
    app = wx.PySimpleApp()   
    frame = DicomDataPathSelFrame(None,-1)
    frame.Show()
    app.MainLoop()
