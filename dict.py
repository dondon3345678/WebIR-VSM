# coding=utf-8
#!/usr/bin/env python
"""
dict.py:
    Convert "inverted-list" to a dict
    key : (vocab_id_1,vocab_id_2)
    value : a list contains (doc_id, frequency)
"""
import sys
import math
import logging
import os
import splitchen
#import jieba
#jieba.initialize()
from collections import defaultdict
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
FORMAT = '%(asctime)-15s %(funcName)s %(message)s'
logging.basicConfig(level=logging.INFO, format = FORMAT)

class BuildDatabase:
    def __init__(self,modelpath,NTCIR_dir):
        self.model_path = modelpath 
        self.NTCIR_dir = NTCIR_dir
        self.vocab = set() # save all term in (vocab_id_1, vocab_id_2)
        self.vocabAll = {}
        self.vocabID = {}
        self.rawtermfreq = defaultdict(dict) # [term][docID] -> frequency
        self.myTFIDF = defaultdict(dict) # self def TF 
        self.nq = defaultdict(int) # [term] -> int : number of documents cotaining term
        self.N = 0; # total number of documents 
        self.doclist = {} # key: docID, value: doc path
        self.bytelength = {}# key: docID, value: length in byte
        self.aval = 0 # average length
        self.slope = 0.75 # slope

    def build(self):
        if os.path.isdir(self.model_path) :
            invertedlist_path = os.path.join(self.model_path, "inverted-file")
            # deal with inverted-file
            logging.info("processing inverted-file....START")
            with open(os.path.abspath(invertedlist_path),'r') as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    vocab_id_1, vocab_id_2, n = line.strip('\n').split(" ")
                    vocab_id_1 = int(vocab_id_1)
                    vocab_id_2 = int(vocab_id_2)
                    n = int(n)
                    # add this term to vocab
                    self.vocab.add((vocab_id_1, vocab_id_2))
                    self.nq[(vocab_id_1, vocab_id_2)] = n
                    for i in range(n):
                        line = f.readline()
                        docID , count = line.strip('\n').split(" ")
                        docID = int(docID)
                        count = int(count)
                        self.rawtermfreq[(vocab_id_1, vocab_id_2)][docID]= count
            # count total number of corpus
            logging.info("processing inverted-file.... END")
            logging.info("processing file-list.........START")
            with open(os.path.abspath(os.path.join(self.model_path, "file-list")), 'r') as f2:
                for index, line in enumerate(f2.readlines()):
                    line = line.strip('\n')
                    self.doclist[index] = line
                    self.N += 1
                    count = 0
                    for event, elem in ET.iterparse(self.NTCIR_dir + line[7:]):
                        if event == 'end':
                            if elem.tag =='p':
                                count += len(elem.text)
                        elem.clear()
                    self.bytelength[index] = count
                for key in self.bytelength.keys():
                    self.aval += self.bytelength[key]
                self.aval = self.aval / self.N
                #print "aval is" , self.aval
            logging.info("processing file-list.........END")
            logging.info("processing vocab-all.........START")
            with open(os.path.abspath(os.path.join(self.model_path, "vocab.all")), 'r') as f3:
                for index, line in enumerate(f3.readlines()):
                    if index != 0:
                        self.vocabID[index] = line.strip('\n').decode('utf-8')
                        self.vocabAll[line.strip('\n').decode('utf-8')] = index
            logging.info("processing vocab.all.........END")

        logging.debug("Dict built over")
    
                
    def getNq(self, term):
        return self.nq[term]

    def getTermFrequency(self, term, docID):
        if docID in self.rawtermfreq[term]:
            return self.rawtermfreq[term][docID]
        else:
            return 0
    def getDocSum(self):
        return self.N
    
    def getVocabID(self, s):
        if s not in self.vocabAll:
            return -1
        else:
            return self.vocabAll[s]
    
    def query2term(self, query):
        stopword = []
        f = open("stopword",'r')
        for words in f.readlines():
            stopword.append(words.decode('utf-8').strip('\n'))
        # use jieba instead
        splitlist = splitchen.splitchen(query)
        #splitlist = jieba.cut(query, cut_all = True)
        # remove stopword in query
        for e in splitlist:
            if e in stopword:
                splitlist.remove(e)
        # start unigram
        uni = []
        for x in splitlist:
            termid = self.getVocabID(x)
            if termid != -1:
                uni.append(termid)
        # start bigram
        unigram = []
        for index in uni:
            unigram.append((index,-1))
        bigram = []
        index = 0
        while index + 1 < len(uni):
            bigram.append((uni[index],uni[index+1]))
            index +=1
        unigram.extend(bigram) # unigram + bigram
        return unigram
    
    def showQuery(self, query):
        for term in query:
            if term[1] == -1:
                print "(",self.vocabID[term[0]].encode('utf-8'),")"
            else:
                print "(",self.vocabID[term[0]].encode('utf-8'),",",self.vocabID[term[1]].encode('utf-8'),")"
    
    def idf(self,term):
        """ top-ten ver: 0 / log(N/nq)"""
        if term not in self.nq:
            return 0 # 4/1 23:55
        else:
            if self.nq[term] == 0:
                # prevent divided by zero
                return 0 # 4/1 23:55
            else:
                return  math.log(self.N/ self.nq[term])#4/1 23:55
    def tf(self,term,docID):
        if term in self.rawtermfreq:
            if docID in self.rawtermfreq[term]:
                f = self.rawtermfreq[term][docID]
                # change parameter to 2 @ 4/6
                k1 = 1.2
                b = 0.75
                return f * (k1 + 1)/ (f + k1 * (1- b + b * self.bytelength[docID] / self.aval))
            else:
                return 0
        else:
            return 0
    def normal(self,vec):
        s = 0
        for x in vec:
            s += x ** 2
        return math.sqrt(s)
"""
if __name__ == "__main__":
    c = BuildDatabase("model")
    c.build()
    query = u'兩稅合一、促進產業升級、促產條例、產升條例、投資抵減、抵減率、租稅優惠、租稅公平、減免、個人股東、高科技產業、創業投資事業、經濟部、財政部、經建會、行政院。'
    q = c.query2term(query)
    print q
"""
