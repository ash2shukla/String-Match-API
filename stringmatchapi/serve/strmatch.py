__author__ = "ash2shukla"

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cs
from pymongo import MongoClient
from collections import Counter
from math import log
from re import sub

dbURL = "mongodb://risky:1234@ds145892.mlab.com:45892/stringdb"

def ret_exists(pid):
    if pid in ret_collection():
        return True
    else:
        return False

def ret_collection():
    c_names = MongoClient(dbURL).stringdb.collection_names()
    c_names.remove('system.indexes')
    c_names.remove('objectlabs-system')
    c_names.remove('objectlabs-system.admin.collections')
    return c_names
    
    
def make_collection(pid):
    try:
        strings = MongoClient(dbURL).stringdb.create_collection(pid)
        if type(strings).__name__ == "Collection":
            return True
        else:
            return "Unexpected"
    except:
        return False

def insert(pid,arg):
    strings = MongoClient(dbURL).stringdb[pid]
    try:
        x=strings.insert({'string':arg})
        if(type(x).__name__ == "ObjectId"):
            return 1
        else:
            return 0
    except:
        return 0

def search_by_tfidf(pid,arg):
    docs=[]
    docs_original=[]
    docs.append(arg)
    docs_original.append(arg)
    strings = MongoClient(dbURL).stringdb[pid]
    for i in strings.find({'string':{'$exists':'true'}}):
        docs_original.append(i['string'])
        docs.append(_prettify_string(i['string'].lower()))
    instance = TfidfVectorizer()
    matrix = instance.fit_transform(docs)
    cosine_matrix = cs(matrix[0:1],matrix)[0]
    retval={'Response Code':200,'Response Message':'Success','Response Data':[]}
    for i in range(1,len(cosine_matrix)):
        if(cosine_matrix[i]*100 > 60):
            retval['Response Data'].append({'stri':docs_original[i],'perc':str(cosine_matrix[i]*100)})
        else:
            pass
    if retval['Response Data'] != []:
        return retval
    else:
        print("Inserting...")
        ret=insert(pid,arg)
        if ret==0:
            return {"Response Code":"501","Response Message":"Could not Insert"}
        elif ret == 1:
            return {"Response Code":"200","Response Message":"Insertion Success"}

def search(pid,arg):
    arg=_prettify_string(arg.lower())
    strings =  MongoClient().stringdb[pid]
    cursor = strings.find()
    retval=[]
    for i in cursor:
        if (_match_str(_prettify_string(i['string'].lower()),arg)>30):
             retval.append(i['string'])
    if retval==[]:
        ret = insert(pid,arg)
        if ret==0:
            return {"Response Code":"501","Response Message":"Could not Insert"}
        elif ret == 1:
            return {"Response Code":"200","Response Message":"Success"}
    return retval

def _prettify_string(string):
    return sub('[^a-z0-9\s+]','',string)

def _convert_to_dict(arg):
    return Counter(arg.split())

def _match_str(arg1,arg2):
    '''
    Find Percentage of existance and multiply it by the fraction of non_existance
    '''
    arg1=_convert_to_dict(arg1)
    arg2=_convert_to_dict(arg2)
    word_len1 = sum(arg1.values())
    word_len2 = sum(arg2.values())
    fract_factor = min(word_len1,word_len2)/max(word_len1,word_len2)
    if(word_len1==max(word_len1,word_len2)):
        greater_str = arg1
        minor_str = arg2
    else:
        greater_str = arg2
        minor_str=arg1
    sum_f_n=0
    sum_f=0
    sum_dne=1
    greater_str=dict(greater_str)
    minor_str=dict(minor_str)
    for i in greater_str.keys():
        try:
            sum_f+=min(greater_str[i],minor_str[i])/max(greater_str[i],minor_str[i])
            sum_f_n+=1
        except KeyError:
            sum_dne+=greater_str[i]
    try:
        retval = ((sum_f/sum_f_n)*(1-log(sum_dne,max(word_len1,word_len2)))*100)
    except ZeroDivisionError :
        retval = 0
    print(retval)
    return retval
