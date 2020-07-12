'''
Created on 2020-07-11

@author: wf
'''
from ptp.event import EventManager, Event
import os
import json

class ConfRef(object):
    '''
    classdocs
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.em=EventManager('confref')
        path=os.path.dirname(__file__)
        self.jsondir=path+"/../sampledata/"
        self.jsonFilePath=self.jsondir+"confref-conferences.json"
        
    def cacheEvents(self):
        ''' initialize me from my json file '''
        with open(self.jsonFilePath) as jsonFile:
            self.rawevents=json.load(jsonFile)
        for rawevent in self.rawevents:
            event=Event()
            event.fromDict(rawevent)
            event.fixAcronym()
            event.source='confref'
            event.url='http://portal.confref.org/list/%s' % rawevent['id']
            self.em.add(event)    
        self.em.store()        
                
    def initEventManager(self):
        ''' initialize my event manager '''
        if not self.em.isCached():
            self.cacheEvents()
        else:
            self.em.fromStore()    
        self.em.extractAcronyms()            
        
        