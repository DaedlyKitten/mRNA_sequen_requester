
import re,threading,requests
from kivymd.app import MDApp
from kivy.lang import Builder 


    #widgets
from kivy.uix.label import Label
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout

    #utilities
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager

from kivymd.theming import ThemableBehavior

from Ks_constantSnack import constantSnack
 


kv=''' 


NavigationLayout:
    ScreenManager:
        id:sm
        MDScreen:
            MDBoxLayout:
                orientation:'vertical'
                CustomToolbar1:
                    id:toolbar
                    MDIconButton:
                        icon: "menu"
                        pos_hint: {"center_y": .5}
                        size_hint:None,None
                        on_release: navdrawer.set_state("open")

                    MDFlatButton:
                        text: 'Get Sequences'
                        pos_hint: {"center_y": .5}
                        font_size: "17sp"
                        on_press: app.getSeq()

                    MDFlatButton:
                        text: 'Align'
                        pos_hint: {"center_y": .5}
                        font_size: "17sp"
                        on_press: app.alignSeq()
                    MDLabel:
                    MDIconButton:
                        icon:'content-save-edit-outline'
                        # text: '--> TXT'
                        pos_hint: {"center_y": .5}
                        on_press: app.saveTXT()

                MDProgressBar:
                    id:progress
                    size_hint_y:0.01
                    color: app.theme_cls.accent_color
                    # pos_hint: {"center_y": 1} 
                    
                # MDBoxLayout:
                #     orientation:'vertical'
                #     adaptiev_height:True

                # MDLabel:
                ScrollView:
                    MDTextField:
                        id: result1
                        multiline:True



    MDNavigationDrawer:
        id: navdrawer
        orientation: "vertical"
        padding:'7dp'

        # MDLabel:
        MDLabel:
            text:'K\\'s \\nmRNA Sequence \\nRequester' #Input url or gene id\\n        to start..' 
            halign:"left"
            font_style:'H5'
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
        
        ScrollView:
            MDList:
                MDTextField:
                    id:input1
                    hint_text:'  Input url or gene id here'
                    required:True
                OneLineListItem:

                OneLineListItem:
                    text:'Start Request'
                    on_press: 
                        navdrawer.set_state("close")
                        app.startTask()
                OneLineListItem:
                    text:'Others'
                    on_press: 
                        navdrawer.set_state("close")
                        result1.text='Put in accession IDs (NM_xxxx) here to "Get Sequences", or \\n\\nPut in gene sequences separated by empty lines to "Align" for common sequences.'
                OneLineListItem:
                    text:''
                    on_press: 
                        app.showCredits()
                        # navdrawer.set_state("close")
                        # result1.text=
                    


<CustomToolbar1>:
    size_hint_y: None
    height: self.theme_cls.standard_increment
    padding: "5dp"
    spacing: "12dp"
    md_bg_color:app.theme_cls.bg_light

    '''



class CustomToolbar1(ThemableBehavior, MDBoxLayout): #RectangularElevationBehavior
    pass


def infoPop(t,m=''):
    MDDialog(title=t,text=m).open()

def infoFloat(m,t=333):
    w.snack.text(text=m,duration=t)


class RNASeqRequester(MDApp):
    title='Kons mRNA Seq Requester'
    accList=[ ]
    accList1=[ ]
    seqList=[ ]
    geneid=''

    url=None
    baseUrl = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

    def build(self):
        self.workingOn=None
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Yellow" 
        return Builder.load_string(kv)

    def on_start(self):
        self.root.ids.navdrawer.set_state('open')
        self.s=self.root.ids
        self.snack=constantSnack(sizeHint=0.15)
        # self.s.input1.focus=True
        # infoFloat('aaa\n111')


    def startTask(self):
        self.geneid=self.s.input1.text.split('/')[-1]
        if self.geneid=='' or not self.geneid.isnumeric():
                infoPop('Invalid Gene ID.','input error')
                return
        if self.url!=None: self.clearWorks()

        url=self.baseUrl+'elink.fcgi?dbfrom=gene&db=nuccore&rettype=acc&id='+self.geneid
        self.startRequest(url)

        self.workingOn='gi'
        self.s.result1.text=''
        self.s.progress.value=10
        infoFloat('[b]Requesting ncbi.nlm.nih.gov...[/b]\n\n>  [i]Please wait...[/i]')


    def startRequest(self,url):
        def errorInfo(req,r): 
            infoPop(str(r))
            print(r)
        # infoFloat('Retrieving '+url,333)
        print(url)
        self.s.progress.value=0
        UrlRequest(url,timeout=200,on_error=errorInfo ,on_success=self.workDone)    


    def workDone(self,req,r):
        print('working on: ',self.workingOn)
        try: r=r.decode()
        except Exception as e: print(e)
        self.s.progress.value=100
        if self.workingOn=='gi':
            try:
                a1=re.search(r'gene_nuccore_refseqrna.+', r,re.DOTALL).group()
            except Exception as e:
                infoFloat('#[b] ID Error:\n[/b]'+str(e))
                return
            giList=re.findall(r'>(\d+)<',a1)
            infoFloat('[b]Retrieving Accessions...[/b] \n\n>  [i]Please Wait...[/i]')
            self.s.result1.text=f'# Got GI list:\n { ", ".join(giList) } \n'

            url=self.baseUrl+'efetch.fcgi?db=nuccore&rettype=acc&id='+'+OR+'.join(giList)
            self.workingOn='acc'
            self.s.progress.value=80
            self.startRequest(url)


        elif self.workingOn=='acc':
            self.accList=r.split('\n')[:-1] #last one is empty string for some reason...
            infoFloat('[b]Done![/b]\n\n[i]Press "Get Sequences" to get sequences.[/i]')
            self.s.result1.insert_text('\n# Retrieved ref RNA: \n'+ '\n'.join(self.accList)+'\n')


        elif self.workingOn=='seqSearch':
            WebEnv=re.search(r'<WebEnv>(.*)</WebEnv>',r).group(1)
            QueryKey=re.search(r'<QueryKey>(.*)</QueryKey>',r).group(1)
            infoFloat(f'[b]Fetching..[/b]\n>  [i]{str(self.accList1)}[/i]')
            u=self.baseUrl+'efetch.fcgi?db=nuccore&query_key='+QueryKey+'&WebEnv='+WebEnv+'&rettype=fasta&retmode=text'
            self.workingOn='seqFetch'
            self.s.progress.value=50
            self.startRequest(u)

        elif self.workingOn=='seqFetch':
            try: self.geneid+=' '+re.search(r'\(([A-Z0-9]+)\)',r).group(1) #(r'>N._[0-9.]+(\D.+?),',r).group(1)
            except Exception: pass
            self.seqList=r.strip().split('\n\n') #[:-1]
            infoFloat('[b]Retrieved Sequences.[/b]\n\n[i]Press "Align" to search for common sequences.[/i]')
            if self.accList==[]: self.accList=self.accList1

            self.s.result1.cursor=(0,0)
            self.s.result1.insert_text('\n'+r+'\n\n')
            self.s.result1.insert_text('Accesion IDs:\n'+', '.join(self.accList1)+'\n\n')
            self.s.result1.cursor=(0,0)


            
    def getSeq(self):
        self.accList1= re.findall(r'([NX]M_[0-9.]+)',self.s.result1.text)     
        if self.accList1==None or self.accList1==[]:
            infoPop('No accessions found.','Put in RNA IDs(NM_xxxx) to fetch sequences or request from gene id.') 
            return
        u=self.baseUrl+'esearch.fcgi?db=nuccore&usehistory=y&term='+'+OR+'.join(self.accList1)
        self.workingOn='seqSearch'
        self.startRequest(u)
        infoFloat(f'[b]Searching sequences..[/b]\n>  [i]{str(self.accList1)}[/i]')
        self.s.progress.value=20


    def alignSeq(self):
        self.s.progress.value=20
        if self.seqList==[ ] and self.workingOn!='acc':
            if self.s.result1.text!='':  
                try: self.seqList=self.s.result1.text.strip().split('\n\n')
                except Exception: pass
            if self.seqList==None or self.seqList==[]:
                infoPop('No sequences found.','Put in gene sequences separated by empty lines to align.') 
                # infoPop('Sequences found: '+str(len(self.seqList)))
                return
        
        try: 
            assert len(self.seqList)>1,'Not enough sequences.\nGet or put in more sequences!'
        except Exception as e:
            infoPop(str(e))
            return
        threading.Thread(target = self.workOnAlign).start()    
        

    def workOnAlign(self):
        def allhasit(seq2,s1):
            for x in seq2:
                if s1 not in x:
                    return False
            return True

        self.seqName=[]
        # print(self.seqList)
        for x,s in enumerate(self.seqList):
            
            try: 
                self.seqName.append(re.search(r'>([XN].+\n)',s).group(1))
                print(self.seqName[x])
                self.seqList[x]=re.sub('>'+self.seqName[x],'',self.seqList[x])
            except Exception as e: infoPop(str(e),'Sequences Error')
            self.seqList[x]=re.sub(r'\n','',self.seqList[x])
   
        bestPos,maxLen,maxLengths=[],0,[]
        s=self.seqList[0]
        l=len(s)
        for curPos in range(l):
            # print(curPos)
            self.s.progress.value=curPos/l*100
            # per='Working: {:.2f} %...\nCurrent maximum length: {}, from posiiton: {}.' .format(maxLen,bestPos)
            infoFloat('{}\nMatching {} sequences...\nCurrent maximum length: {}, posiitons: {}.' .format(curPos,len(self.seqList),maxLen,str(bestPos)))
            for sameLen in range(20,l-curPos,5):  #jumping for faster matching
                if allhasit(self.seqList, s[curPos:curPos+sameLen] ):
                    if sameLen>maxLen:
                        maxLen=sameLen
                        if curPos not in bestPos: 
                            bestPos.append(curPos)
                            maxLengths.append(sameLen)
                else:    
                    break 


        otherpositions=[]
        for n in [2,3,4]:
            try: otherpositions.append(str(bestPos[-n])+' to '+str(bestPos[-n]+maxLengths[-n]))
            except Exception: pass
        theBestPos=bestPos[-1]
        infoFloat('Done !\n\n[i]Press ->TXT to save result to text file.[/i]',10)
        self.s.result1.cursor=(0,0)
        try:     
            self.s.result1.insert_text(f'\n# Gene {self.geneid}   {re.search(r"[XN]._[0-9.]+",self.seqName[0]).group()}\n' )
        except Exception as e: print(e)
        self.s.result1.insert_text(f'\n== Maximum alignment from position: {theBestPos} to {theBestPos+maxLen} (+/-5). \n== Other positions:\n{ "; ".join(otherpositions) }\n')
        self.s.result1.insert_text(f'\n== The common sequence of {len(self.seqList)} sequences:\n{s[theBestPos:theBestPos+maxLen]}\n\n')
        self.s.result1.cursor=(0,0)

        self.seqList=[]
        self.accList=[]

        
    

    def saveTXT(self):
        try:
            # a=self.geneid   =a[:50]+'.txt' if len(a)>50 else a+'.txt'
            path=self.geneid + '.txt'

            print(self.s.result1.text,file=open('./'+path,'w')) #'\n\n----------\n'.join(self.record)
        except Exception as e:
            infoPop(str(e),'txt error')
        else: 
            infoPop(f'Saved to {path}.')


    def clearWorks(self):
        self.workingOn=None
        self.url=None
        self.accList=[ ]
        self.seqList=[ ]
        self.s.progress.value=0

    def showCredits(self):
        infoPop('Seq Requester.\nWritten in Python3.7, Kivy2.0rc4\nDeployed with pyinstaller.','https://github.com/DaedlyKitten 2020.3.')






# if __name__ == '__main__':
w=RNASeqRequester()
w.run()
