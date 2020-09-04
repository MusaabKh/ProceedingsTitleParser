'''
Created on 2020-09-04

@author: wf
'''
from collections import Counter
class UML(object):
    '''
    UML diagrams via plantuml
    
    '''

    skinparams="""
' BITPlan Corporate identity skin params
' Copyright (c) 2015 BITPlan GmbH
' see http://wiki.bitplan.com/PlantUmlSkinParams#BITPlanCI
' skinparams generated by com.bitplan.restmodelmanager
skinparam note {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam component {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam package {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam usecase {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam activity {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam classAttribute {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam interface {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam class {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
skinparam object {
  BackGroundColor #FFFFFF
  FontSize 12
  ArrowColor #FF8000
  BorderColor #FF8000
  FontColor black
  FontName Technical
}
hide Circle
' end of skinparams '
"""

    def __init__(self, debug=False):
        '''
        Constructor
        Args:
            debug(boolean): True if debug information should be shown
        '''
        self.debug=debug
        
    def generalizeColumn(self,tableList,colName):
        ''' 
        remove the column with the given name from all tables in the tablelist and
        return it
        
        Args:
            tableList(list): a list of Tables
            colName(string): the name of the column to generalize
        
        Returns:
            string: the column having been generalized and removed
        '''
        gCol=None
        for table in tableList:
            for col in table['columns']:
                if col['name']==colName:
                    gCol=col.copy()
                    # no linking yet @FIXME - will need this later
                    if 'link' in gCol:
                        gCol.pop('link')
                    # is generalization protected for this column?
                    if not 'special' in col or not col['special']:
                        table['columns'].remove(col)
        return gCol                
        
    def getGeneral(self,tableList,name):
        '''
        derive a general table from the given table list
        Args:
            tableList(list): a list of tables
            name(string): name of the general table
            
        Returns:
            at table dict for the generalized table
        '''
        general={'name':name,'columns':[]}
        colCount=Counter()
        for table in tableList:
            for col in table['columns']:
                columnId="%s.%s" % (col['name'],col['type'])
                if self.debug:
                    print (columnId) 
                colCount[columnId]+=1
        for columnId,count in colCount.items():
            if count==len(tableList): 
                colName=columnId.split('.')[0]
                generalCol=self.generalizeColumn(tableList, colName)
                general['columns'].append(generalCol)    
        return general
            
    def tableListToPlantUml(self,tableList,title=None,packageName=None,generalizeTo=None,withSkin=True):
        '''
        convert tableList to PlantUml notation
        
        Args:
            tableList(list): the tableList list of Dicts from getTableList() to convert
            title(string): optional title to be added
            packageName(string): optional packageName to be added
            generalizeTo(string): optional name of a general table to be derived
            withSkin(boolean): if True add default BITPlan skin parameters 
            
        Returns:
            string: the Plantuml notation for the entities in columns of the given tablelist
        '''
        uml=""
        indent=""
        inherit=""
        if title is not None:
            uml+="title\n%s\nend title\n" % title
        if packageName is not None:
            uml+="package %s {\n" % packageName
            indent="  "
        if generalizeTo is not None:
            generalTable=self.getGeneral(tableList,generalizeTo)
            for table in tableList:
                inherit+="%s%s <|-- %s\n" % (indent,generalizeTo,table['name'])
            tableList.insert(0,generalTable)
        for table in tableList:
            colUml=""
            for col in table['columns']:
                mandatory="*" if col['notnull']==1 else ""
                pk="<<PK>>" if col['pk']==1 else ""
                colName=col['name']
                colType=col['type']
                if 'link' in col:
                    colName=col['link']
                colUml+="%s %s%s : %s %s\n" % (indent,mandatory,colName,colType,pk)
            tableName=table['name']    
            if 'notes' in table:
                uml+="Note top of %s\n%s\nEnd note\n" % (tableName,table['notes'])
            uml+="%sclass %s << Entity >> {\n%s%s}\n" % (indent,tableName,colUml,indent)
        uml+=inherit    
        if packageName is not None:
            uml+="}\n"
        if withSkin:
            uml+=UML.skinparams    
        return uml
    
    def mergeSchema(self,schemaManager,tableList, title=None,packageName=None,generalizeTo=None,withSkin=True):
        '''
        merge Schema and tableList to PlantUml notation
        
        Args:
            schemaManager(SchemaManager): a schema manager to be used
            tableList(list): the tableList list of Dicts from getTableList() to convert
            title(string): optional title to be added
            packageName(string): optional packageName to be added
            generalizeTo(string): optional name of a general table to be derived
            withSkin(boolean): if True add default BITPlan skin parameters 
            
        Returns:
            string: the Plantuml notation for the entities in columns of the given tablelist

        '''
        if schemaManager is not None:
            for table in tableList:
                if 'schema' in table:
                    schema=schemaManager.schemasByName[table['schema']]
                    url="%s/%s" % (schemaManager.baseUrl,schema.name)
                    url=url.replace(" ", "_") # mediawiki
                    instanceNote=""
                    if 'instances' in table:
                        instanceNote="\n%d instances " % (table['instances'])
                    table['notes']="""[[%s %s]]%s""" % (url,schema.name,instanceNote)
                    for col in table['columns']:
                        colName=col['name']
                        if colName in schema.propsByName:
                            prop=schema.propsByName[colName]
                            if prop.iri is not None:
                                tooltip=""
                                if prop.definition is not None:
                                    tooltip="{%s}" % prop.definition
                                col['link']="[[%s%s %s]]" % (prop.iri,tooltip,colName)
                                col['special']=True # keep column even if generalized
                    pass
        plantuml=self.tableListToPlantUml(tableList, title=title,packageName=packageName, generalizeTo=generalizeTo, withSkin=withSkin) 
        return plantuml   
        