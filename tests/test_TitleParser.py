'''
Created on 2020-06-20

@author: wf
'''
import unittest
from ptp.titleparser import TitleParser, Title, \
    ProceedingsTitleParser
from collections import Counter
from ptp.plot import Plot
import networkx as nx
import os
import getpass
from ptp.openresearch import OpenResearch

class TestProceedingsTitleParser(unittest.TestCase):
    """ test the parser for Proceedings titles"""

    debug=False
    def setUp(self):
        path=os.path.dirname(__file__)
        self.titlesdir=path+"/../sampledata/"
        pass

    def tearDown(self):
        pass

    def getTitleParser(self,name,expectedLines,mode="wikidata"):
        titleFile=self.titlesdir+name
        tp=TitleParser.fromFile(titleFile,mode)
        tp.name=name
        print ("%6d lines found at least %6d expected" % (len(tp.lines),expectedLines))
        self.assertTrue(expectedLines<=len(tp.lines))
        return tp 
    
    def getParser(self):
        return ProceedingsTitleParser.getInstance()
       
    def tryParse(self,line,parser,tc,qref=None,doprint=False):
        """ try parsing the given line and return the title"""
        title=Title(line,parser.grammar)
        if qref is not None and self.debug:
            print (qref) 
        if doprint:    
            print (line)
        try: 
            title.pyparse()
            if self.debug:
                title.dump()
            if doprint:    
                print (title.metadata())    
            tc["success"]+=1
            return title
        except Exception as ex:
            tc["fail"]+=1
            print (ex)
            return None
        
    def testExamples(self):
        ''' test specific examples for parsing success '''
        titlelines=[
            "Computer-assisted modeling of receptor-ligand interaction. Theoretical aspects and applications to drug design. Proceedings of the 1988 OHOLO Conference. Eilat, Israel, April 24-28, 1988",
            "Advances in chronic kidney disease 2009. Proceedings of the 11th International Conference on Dialysis. January 28-30, 2009. Las Vegas, Nevada, USA",
            "Nutrition in Clinical Management of HIV-Infected Adolescents (>14 y old) and Adults including Pregnant and Lactating Women: What Do We Know, What Can We Do, and Where Do We Go from Here? Proceedings of a conference held in Washington, DC, July 26-28",
            "Abstracts of the Official Proceedings of the 11th Annual Meeting of the American Society of Breast Surgeons. April 28-May 2, 2010. Las Vegas, Nevada, USA",
            "Old and New Dopamine Agonists in Parkinson's Disease: a Reappraisal. Proceedings of the LIMPE Seminar, 26-28 February, Pisa, Italy, 2009",
            "The Proceedings of the 97th Tohoku Regional Meeting of the Japanese Society of Neurology",
            "Subchondral Pathology: Proceedings of the International Consensus Meeting on Cartilage Repair of the Ankle",
            "Scientific Proceedings of the Twenty-seventh Annual Meeting of the American Association of Pathologists and Bacteriologists",
            "Bulletins et Mémoires de la Société Française d'Ophtalmologie: Proceedings of 1980 Congress",
            "British Pædiatric Association: Proceedings of the First Annual General Meeting",
            "Advances in Medical Computing (Proceedings of the 3rd International Symposium on Computers in Medicine)",
            "Red Drum Aquaculture, Proceedings of a Symposium on the Culture of Red Drum and Other Warm Water Fishes",
            "A summary of the Proceedings of the Twelfth International Symposium on the Neurobiology and Neuroendocrinology of Aging, Bregenz, Austria July 27-August 1, 2014.",
            "[Update on vaccine research. Proceedings of the 15th annual conference on vaccine research organized by the National Foundation for Infectious Diseases].",
            "Very broad Markush claims; a solution or a problem? Proceedings of a round-table discussion held on August 29, 1990.",
            "Abstracts From the Proceedings of the 2015 Annual Meeting of the Clerkship Directors of Internal Medicine (CDIM).",
            "Christo Deltshev & Pavel Stoev (eds) (2006): European Arachnology 2005, Acta zoologica bulgaria, Suppl. No. 1; Proceedings of the 22nd European Colloquium of Arachnology, Blagoevgrad, Bulgaria, 1-6 August 2005",
            "(L.) Bricault and (M.J.) Versluys Eds Power, Politics, and the Cults of Isis: Proceedings of the Vth International Conference of Isis Studies (Religions in the Graeco-Roman World 180). Leiden: Brill, 2014. Pp. xvii + 364. €139/$180. 9789004277182",
            "Kunaitupii: Coming Together on Native Sacred Sites—Their Sacredness, Conservation and Interpretation. Brian O. K. Reeves and Margaret A. Kennedy, editors. Proceedings of the First Joint Meeting of the Archaeological Society of Alberta and the Monta",
            "Jan Apel and Kjel Knutsson: Skilled Production and Social Reproduction. Aspects of Traditional Stone‐Tool Technologies. Proceedings of a Symposium in Uppsala, August 20–24, 2003",
            "Developing ambient intelligence - proceedings of the first international conference on ambient intelligence developments.",
            #"Sea Lice 2003 - Proceedings of the sixth international conference on sea lice biology and control"
            #'Tagungsband des 17. Workshops "Software Engineering im Unterricht der Hochschulen" 2020 (SEUH 2020),Innsbruck, Österreich, 26. - 27.02.2020.'
            ]
        parser=self.getParser()
        tc=Counter()
        for line in titlelines:
            self.tryParse(line, parser, tc)
        self.assertEqual(tc["success"],len(titlelines))   
       
    def testAcronymParsing(self):
        ''' test acronym parsing '''
        title=Title("(ATAED 2020)",ProceedingsTitleParser.acronymGroup)
        title.pyparse()
        md=title.metadata()
        self.assertTrue("acronym" in md)
        self.assertEquals("ATAED 2020",md["acronym"])
          
        
    def testExampleResult(self):
        ''' test result of example ''' 
        titlelines=[
            'Proceedings of the Thirty-First AAAI Conference on Artificial Intelligence, February 4-9, 2017, San Francisco, California, USA',
            'Selected proceedings of the 2009 Summit on Translational Bioinformatics.',
            'Proceedings of the International Workshop on Algorithms & Theories for the Analysis of Event Data 2020 (ATAED 2020),virtual workshop, June 24, 2020']   
        expected=[
            {'enum': 'Thirty-First', 'prefix': 'AAAI', 'event': 'Conference', 'topic': 'Artificial Intelligence', 'month': 'February', 'daterange': '4 - 9', 'year': '2017', 'city': 'San Francisco', 'province': 'California', 'country': 'USA'},
            {'event': 'Summit', 'extract': 'Selected', 'topic': 'Translational Bioinformatics','year': '2009'},
            {'event': 'Workshop', 'location':'virtual','scope': 'International', 'topic': 'Algorithms & Theories for the Analysis of Event Data 2020','acronym':'ATAED 2020'}
        ]
        parser=self.getParser()
        tc=Counter()
        index=0
        for line in titlelines:
            title=self.tryParse(line, parser, tc)
            metadata=title.metadata()
            print(metadata)
            self.assertEqual(expected[index],metadata)
            index+=1
        self.assertEqual(tc["success"],len(titlelines))
        
    def doTestParser(self,tp,minSuccess,limit=100):
        ''' general test Parsing function ''' 
        parser=self.getParser()
        tc=Counter()
        lineCount=0
        for line in tp.lines:
            qref=None
            if "q" in line:
                qref=line["q"]
            lineCount=lineCount+1    
            self.tryParse(line["title"],parser,tc,qref=qref,doprint=lineCount<=limit)
        print(tc.most_common(2))   
        self.assertGreater(tc["success"], minSuccess)     
               
    def testPyParseWikiData(self):
        ''' test pyparsing parser '''
        tp=self.getTitleParser("proceedings-wikidata.txt",16000)
        self.doTestParser(tp,15500)
        
    def testCEUR_WS(self):
        ''' test pyparsing parser with CEUR-WS dataset '''
        tp=self.getTitleParser("proceedings-ceur-ws.txt",2629,mode='CEUR-WS')
        self.doTestParser(tp,2280)
        
    def testDBLP(self):
        ''' test pyparsing with DBLP dataset '''
        tp=self.getTitleParser("proceedings-dblp.txt",14207,mode='dblp')
        self.doTestParser(tp,13700)
           
     
    def testSeriesEnumeration(self):
        ''' test getting most often used series enumerations of Proceeding Events '''
        tp=self.getTitleParser("proceedings-wikidata.txt",16000)
        d=ProceedingsTitleParser.getDictionary()
        tc=Counter()
        for line in tp.lines:
            title=Title(line["title"],dictionary=d)
            title.parse()
            if title.enum is not None:
                print ("%d: %s" % (title.enum,line))
                print ("    %s" % title.info)
                tc[title.enum]+=1
        print(tc.most_common(250))     
           
    def doTestTitleParser(self,tp,em,showHistogramm=False):
        ''' test the title parser '''       
        d=ProceedingsTitleParser.getDictionary()
        tc=Counter()
        typeCounters={}
        kc=Counter()
        known=0
        total=0
        tclist=[]
        for line in tp.lines:
            title=Title(line["title"],d)
            tclist.append(len(title.tokens))
            for token in title.tokens:
                total+=1
                dtoken=d.getToken(token)
                if dtoken is None:
                    if token in em.eventsByAcronym:
                        dtoken={}
                        dtoken["type"]="acronym"
                        dtoken["label"]=token
                if dtoken is None:
                    tc[token]+=1
                else: 
                    known+=1
                    kc[token]+=1
                    tokenType=dtoken["type"]
                    if tokenType in typeCounters:
                        typeCounter=typeCounters[tokenType]
                    else:
                        typeCounter=Counter()
                        typeCounters[tokenType]=typeCounter
                    label=dtoken["label"]    
                    typeCounter[label]+=1        
        
        for tokenType in typeCounters:
            typeCounter=typeCounters[tokenType]
            print ("%s: %s" % (tokenType,typeCounter.most_common(5)))
            
        print ("""
{| class="wikitable"
|-
! type !! count !! most common examples: count""")
        for tokenType in sorted(typeCounters):
            typeCounter=typeCounters[tokenType]
            print ("|-")
            mc=typeCounter.most_common(5)
            mcs=""
            delim=""
            for item,count in mc:
                mcs=mcs+"%s%s: %d" % (delim,item,count)
                delim=", "
            print ("|%s || %d || %s" % (tokenType,d.countType(tokenType),mcs))
        print ("|}")    
             
        print("known: %d of %d %5.1f%%" % (known,total,known/total*100))
        print(tc.most_common(250))   
        print(kc.most_common(250))     
        if showHistogramm:
            title=tp.name.replace(".txt","")
            plot=Plot(tclist,title)
            plot.hist(mode="save")
        pass
  
    def testTitleParser(self):
        ''' test reading the titles '''
        showHistogram=True
        em=OpenResearch.getEventManager()
        for tp in [
                self.getTitleParser("proceedings-ceur-ws.txt",2629,mode='CEUR-WS'),
                self.getTitleParser("proceedings-dblp.txt",14207,mode='dblp'),
                self.getTitleParser("proceedings-wikidata.txt",16000)
            ]:
            self.doTestTitleParser(tp,em,showHistogram)   
      
    def testGraph(self):
        g=nx.Graph()
        g.add_edge('A', 'B', weight=4)
        #nx.write_yaml(g, 'g_test1.yaml')
        #nx.write_graphml_lxml(g,'g_test1.graphml')
        
    def testDictionary(self):
        ''' test the dictionary '''
        d=ProceedingsTitleParser.getDictionary()
        print (d.tokens)
        d.addEnums()
        d.addYears()
        print (d.tokens)
        d.write()
        
    def testError(self):
        ''' test error handling according to https://github.com/WolfgangFahl/ProceedingsTitleParser/issues/4 '''
        ptp=ProceedingsTitleParser.getInstance()
        dictionary=ProceedingsTitleParser.getDictionary()
        # get the open research EventManager
        em=OpenResearch.getEventManager()  
        titles='Tagungsband des 17. Workshops "Software Engineering im Unterricht der Hochschulen" 2020 (SEUH 2020),Innsbruck, Österreich, 26. - 27.02.2020.'
        tc,errs,result=TitleParser.fromLines(ptp,dictionary,em,titles)  
        # there should be a faile dline
        self.assertEquals(1,tc["fail"])
        self.assertEquals(1,len(errs))
        err=errs[0]
        self.assertTrue("Expected" in str(err))
        self.assertEquals(1,len(result))
        
    def testNERMode(self):
        ''' test named entity recognition mode '''
        ptp=ProceedingsTitleParser.getInstance()
        dictionary=ProceedingsTitleParser.getDictionary()
        em=OpenResearch.getEventManager()
        titles='ATVA 2020 18th International Symposium on Automated Technology for Verification and Analysis'
        tc,errs,result=TitleParser.fromLines(ptp,dictionary,em,titles)  
        print (tc)
        print (errs)
        print (result)
        # make sure we have exactly one result
        self.assertEquals(1,len(result))
        title=result[0]
        print (title)
        print (title.info)
        print (title.metadata())
        print (title.notfound)
        # make sure we found the relevant event
        self.assertTrue(title.event is not None)
        
   
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()