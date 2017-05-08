# coding=utf-8
import dict
import splitchen
import math
import os
import logging
import sys
import re
#import jieba 
#jieba.initialize()
FORMAT = '%(asctime)-15s %(funcName)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format = FORMAT)
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

if __name__ == '__main__':
    # Generate Database
    RF = False
    model_dir = ""
    NTCIR_dir = ""
    query_xml = ""
    ranked_list = ""
    if sys.argv[1] == "-r":
        RF = True
        query_xml = sys.argv[3]
        ranked_list = sys.argv[5]
        model_dir = sys.argv[7]
        NTCIR_dir = sys.argv[9]
    else:
        RF = False
        query_xml = sys.argv[2]
        ranked_list = sys.argv[4]
        model_dir = sys.argv[6]
        NTCIR_dir = sys.argv[8]
    db = dict.BuildDatabase(model_dir,NTCIR_dir)
    db.build()
    
    # read query file and start to query
    root = ET.parse(query_xml).getroot()
    out = open(ranked_list,'w')
    out.write('query_id,retrieved_docs\n')
    logging.info("Query start")
    for topic in root:
        qID = ""
        score = []
        query = []
        text = []
        for elem in topic:
            if elem.tag == 'number':
                qID = elem.text[-3:]
                logging.info("Processing query id = %s", qID)
            elif elem.tag == 'concepts':
                text = elem.text.strip(u'。').split(u'、')
                #query.extend(db.query2term(elem.text.strip('\n').strip(u'、').strip(u'。')))
            else :
                text = re.split(u'、|，|。',elem.text)
            for term in text:
                query.extend(db.query2term(term))
        prod = 0
        #db.showQuery(query)
        vec = []
        qc = {}
        idf = {}
        for term in query:
            qc[term] = query.count(term)
            idf[term] = db.idf(term)
        for term in query:
            vec.append(qc[term])
        norm = db.normal(vec)
        for docID in range(len(db.doclist)):
            #logging.info("calculate %d docID's score",docID)
            prod = 0
            for term in query:
                wq = qc[term]/norm * idf[term]
                #wq = (500 + 1) * query.count(term) / (500 + query.count(term))
                wd = db.tf(term, docID) * idf[term]
                prod += wq * wd
            score.append((docID, prod))
        rank = sorted(score, key = lambda x:x[1], reverse=True)
        top =rank[0:100]
        #relevance feedback
        if RF :
            logging.info("start RF")
            all_term = []
            relevant = top[0:5]
            for (docID,score) in relevant:
                fake = ET.parse(NTCIR_dir + db.doclist[docID][7:]).getroot()
                for doc in fake:
                    for elem in doc:
                        if elem.tag == 'title':
                            text = re.split(u'、|，|。|　',elem.text)
                            for term in text:
                                all_term.extend(db.query2term(term))
                        if elem.tag == 'text':
                            for p in elem:
                                text = re.split(u'、|，|。|　|：|；',p.text)
                                for term in text:
                                    all_term.extend(db.query2term(term))
            unique_term_set = set(all_term)
            term_score = []
            for e in unique_term_set:
                n = 0
                for (docID,prod) in relevant:
                    if docID in db.rawtermfreq[e]:
                        n+=1
                term_score.append((e,n * db.idf(e)))

            term_rank = sorted(term_score, key = lambda x:x[1], reverse= True)
            top_term = term_rank[0:10]
            for (term, score) in top_term:
                query.append(term)
            # query extend over
            # re-query
            logging.info("requery!")
            prod = 0
            #db.showQuery(query)
            vec = []
            score = []
            qc = {}
            idf = {}
            for term in query:
                qc[term] = query.count(term)
                idf[term] = db.idf(term)
            for term in query:
                vec.append(qc[term])
            norm = db.normal(vec)
            for docID in range(len(db.doclist)):
                #logging.info("calculate %d docID's score",docID)
                prod = 0
                for term in query:
                    wq = qc[term]/norm * idf[term]
                    wd = db.tf(term, docID) * idf[term]
                    prod += wq * wd
                score.append((docID, prod))
            rank = sorted(score, key = lambda x:x[1], reverse=True)
            # clear old top and create new top
            top = []
            top =rank[0:100]
        #end of RF 
        strout = qID + ","
        for (id, score) in top:
            strout +=  db.doclist[id][-15:].lower() + " "
        out.write(strout[:len(strout)-1] + "\n")
        #sys.exit()
    logging.info("Query Finished!")
