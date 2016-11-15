#! /usr/bin/env python
# -*- coding:utf8 -*-

import wx
from wx.lib import newevent

DispatchEvent,EVT_DISPATCH = newevent.NewEvent()

class GenericDispatchMix(object):
    """ A Mixin class to to respond to the customized event."""
    def __init__(self):
        """event binder initialization"""
        EVT_DISPATCH(self,self.OnDispatchEvent)
        
    def OnDispatchEvent(self,event):
        """handle the event"""
        event.method(*event.arguments)
    
    def ThreadSafeDispatch(self,method,*arguments):
        """a thread-safe caller to handle the update of GUI"""
        wx.PostEvent(self,DispatchEvent(method=method,arguments=arguments))