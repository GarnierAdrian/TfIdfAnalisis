from tkinter import *
import os
import numpy as np
import gc
import random
import pickle
import time
import math
from functools import partial

class Search():

    def __init__(self):
        self.query = ""
        self.idxQuery = np.array([])
        self.e = 1
        self.k = 1
        self.Dqu = {}
        self.indPath = "\\index"
        self.archPath= ""

    def main(self, query, e, k, isAmazon, docPath):
        self.query = query
        self.e = e
        self.k = k
        self.indexar()
        if isAmazon:
            self.indPath = '\\indexA'
        self.archPath = docPath
            
        return self.recorrer()

    def indexar(self):
        Dq = {}
        p = [',','.',';',':','-','/','!','?']
        
        
        #divide en terminos
        terms = self.query.split(" ")

        #Calcula tf
        pos = 0
        for term in terms:
            #quita puntuacion
            l = len(term)
            if term[l-1] in p:
                term = term[:l-1]
                terms[pos] = term

            #lo agrega al diccionario
            if len(Dq) == 0:
                Dq[term] = 1
            else:
                if term in Dq:
                    Dq[term] = Dq[term]+1
                    terms.remove(term) #quita el repetido
                else:
                    Dq[term] = 1
            pos += 1

        #Multiplica por el IDF
        idf = {}
        with open("idf.txt","rb") as fp:
            idf = pickle.load(fp)
            fp.close()

        arr = []
        for k in terms:
            if k in idf:
                Dq[k] = Dq[k] * idf[k]  
            else:
                del Dq[k]

        #Crea el vecotr TF-IDF:
        arr = []
        terms = Dq.items()
        for t in terms:
            arr.append(Dq[t[0]])
        self.idxQuery = np.array(arr)
        self.Dqu = Dq
        print(self.idxQuery)
        

    def cosineSimilarity(self,doc):
        if np.count_nonzero(doc)== 0:
            return 0
        cos = self.idxQuery.dot(doc)/(math.sqrt((self.idxQuery**2).sum())*math.sqrt((doc**2).sum()))
        return cos

    def evalDoc(self,doc):
        #Saca en vector palabras que ocupa
        vect = []
        terms = self.Dqu.items()
        for t in terms:
            if t[0] in doc:
                vect.append(doc[t[0]])
            else:
                vect.append(0)
        v = np.array(vect)
        
        # calcula similitud
        cos = self.cosineSimilarity(v)
        return cos

    def recorrer(self):
        time1 = time.time()
        #recorro todos los indices 
        result = []
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(ROOT_DIR+ self.indPath):
            for file in files:
                with open(os.path.join(root, file), "rb") as auto:
                    doc = pickle.load(auto)
                    t = (len(doc)) * (self.e/100)
                    t = int(t)
                    random.shuffle(doc) #probabilistico
                    for j in range(t): ##Cambio
                        i = doc[j] ##Cambio
                        cos = self.evalDoc(i[1])
                        name = (os.path.join(root, i[0])).replace( self.indPath,self.archPath)

                        if len(result) <= self.k:
                            result.append([name,cos])
                            result = sorted(result, key=lambda x: x[1], reverse=True)#
                        
                        elif cos > result[self.k-1][1]: ##self.k-1
                            del(result[self.k-1])
                            result.append([name,cos])
                            result = sorted(result, key=lambda x: x[1], reverse=True)#
        time2 = time.time()
        print(time2 - time1)
        return result
                        

        
        

class Application(Frame):
    
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.isAmazon = True
        self.docPath = "\\smallset" ## <-AQUI!!!!!!!!!!!!!!!!
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.title1 = Label(self, text="Indexing with TF-IDF:", font = "Times 15")
        self.title1.grid(column=0, row=0,sticky=W)

        self.path = Entry(self, text="Document's path", width = 50)
        self.path.grid(column=0, row=1)

        self.indexBtn = Button(self, text="Index", command = self.indexD)
        self.indexBtn.grid(column=1, row=1)

        self.title2 = Label(self, text="Search Engine:",font = "Times 15")
        self.title2.grid(column=0, row=2,sticky=W)

        self.kEntry = Spinbox(self, from_=1, to=100)
        self.kEntry.grid(column=0, row=3, sticky=E)

        self.kLabel = Label(self, text="k")
        self.kLabel.grid(column=1, row=3)
        
        self.errorEntry = Spinbox(self, from_=50, to=100)
        self.errorEntry.grid(column=0, row=4, sticky=E)

        self.kLabel = Label(self, text="% Error")
        self.kLabel.grid(column=1, row=4)

        self.query = Entry(self, width=50)
        self.query.grid(column=0, row=5)

        self.searchBtn = Button(self, text="Search", command = self.search)
        self.searchBtn.grid(column=1, row=5)

        self.statusLbl = Label(self, text=" ")
        self.statusLbl.grid(column=0, row=6)
        
        
    def indexD(self):
        self.statusLbl["text"] = "Indexing..."
        self.isAmazon = False
        dPath = self.path.get()
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.docPath = dPath.replace(ROOT_DIR,"")
        
        #llama funcion de indexar
        print(dPath)
        index(dPath)
        

    def load(self):
        self.statusLbl["text"] = "Loading..."
        #carga a memoria los indices

    def search(self):
        self.statusLbl["text"] = "Searching..."
        docQuery = self.query.get()
        k = int(self.kEntry.get())
        error = int(self.errorEntry.get())

        #llama a buscar con el query, k, error
        #retorna una lista de titulos de documentos para abrirlos

        srch = Search()
        result = srch.main(docQuery, error, k, self.isAmazon, self.docPath)
        
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        for i in range(k): #in lista de titulos de documentos
            root = result[i][0]
            title = root.replace(ROOT_DIR,"")
            print(title,"cos: ",result[i][1])
            self.label = Label(self, text=title)
            self.label.grid(column=0, row=7+i)

            
            self.btn = Button(self, text="Open", command = partial(self.openD,root))
            self.btn.grid(column=1, row=7+i)

    def openD(self, title):
        self.statusLbl["text"] = "Opening document..."
        os.startfile(title)

def index(fpath):
    idf = {}
    tf = []
    f = 0.0
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    #print(ROOT_DIR)
    fname = fpath.replace(ROOT_DIR, "")
    #print(fname)
    ipath = ROOT_DIR + "\\index"
    if not os.path.exists(ipath):
        os.makedirs(ipath)
    for root, dirs, files in os.walk(fpath,topdown=True):
        c = 0
        for dire in dirs:
            if not os.path.exists(root.replace(fname,"\\index")+"\\"+dire):
                os.makedirs(root.replace(fname,"\\index")+"\\"+dire)
        for file in files:
            tf.append((file,tfidf(idf,root + "\\" + file)))
            c += 1
            if c % 10000 == 0:
                saveBulk(file,tf,root.replace(fname,"\\index"))
                print("saving")
                del tf[:]
                gc.collect()
        if tf:
            saveBulk(file,tf,root.replace(fname,"\\index"))

        print("\n")
    gc.collect()
    f = float(c)
    for c in idf:
        idf[c] = f/idf[c]
        #print(idf[c])
        idf[c] = math.log10(idf[c])
    f = open("idf.txt",'wb')
    pickle.dump(idf, f)
    c = 0
    for root, dirs, files in os.walk(ipath,topdown=True):
        for file in files:
            aux3 = []
            with open(root + "\\" +file,"rb") as fp:
                data = pickle.load(fp)
                for aux in data:
                    name, dicti = writeFile(aux[0],fname,idf,aux[1],root)
                    aux3.append((name, dicti))
                saveBulk(file,aux3,root)
                del aux3[:]
                gc.collect()

    print("indexado")

            

def saveBulk(file,aux2,root):
    f= open(root+"\\"+file,'wb')
    pickle.dump(aux2,f)
    f.close()

            
def writeFile(file,fname,idf,aux2,root):
    for i in aux2:
        aux2[i] = aux2[i] * idf[i]
    return(file, aux2)
    

def saveBigDic(file,fname,aux2,root):
    pass


def tfidf(idf, filename):
    file = open(filename,'r')
    aux = []
    tfd = {}
    words = file.read()
    words = re.split("[,\n \-!?:.\"]+",words)
    x = []
    for i in words:
        x.extend(i.split("\\"))
    for i in x:
        if i != '':
            if i in tfd:
                tfd[i] += 1
            else:
                tfd[i] = 1.0

            if i not in idf:
                idf[i] = 1.0
            else:
                if i not in aux:
                    idf[i] += 1
                    aux.append(i)

    for i in tfd:
        tfd[i]=tfd[i]/len(x)
    return(tfd)
        

root = Tk()
root.title("Mini Google")
app = Application(master=root)
app.mainloop()


    
