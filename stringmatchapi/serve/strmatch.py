__author__ = "ash2shukla"

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as cs
from pymongo import MongoClient
from collections import Counter
from math import log
from re import sub
from urllib import urlretrieve as ur
from xlrd import open_workbook
from xlrd.book import Book
from xlwt import Workbook
from json import dumps
from pprint import pprint

dbURL = "mongodb://localhost:27017/"
filebaseURL = "http://tbcs.spikeway.com/bulkfile/"

def getFile(url,pid,spid,isview):
    lst = []
    export = Workbook()
    export_sheet = export.add_sheet('match')
    book = open_workbook(ur(filebaseURL+url)[0])
    if isinstance(book,Book):
        sheet = book.sheet_by_index(0)
        for i in range(sheet.nrows):
            lst.append(sheet.cell_value(i,0))
        instance = TfidfVectorizer()
        matrix = instance.fit_transform(lst)
        cosine_matrix = cs(matrix,matrix)
        k = 0
        outer_arr = []
        for i in range(len(cosine_matrix)):
            fl = list(cosine_matrix[i])
            incr = 0
            n_lst = lst[:i]+lst[i+1:]
            dic = {}
            for j in fl[:i]+fl[i+1:]:
                if j*100 > 80:
                    dic['string']=lst[i]
                    dic['matched_with']=n_lst[incr]
                    dic['percent']=str(j*100)[:6]
                    k+=1
                    outer_arr.append(dic)
                    print i,incr
                incr += 1
        if len(outer_arr) == 0:
            retval = pushBulk(lst,pid,spid)
            if retval == -1 :
                return dumps({"Reponse Code":"200","Response Message":"Unsuccessful.",'Response Data':''})
            else:
                return dumps({'Response Code':200,'Response Message':'Success','Response Data':retval})
        else:
            try:
                return dumps({'Response Code':200,'Response Message':'Success','Response Data in file':outer_arr})
            except:
                return dumps({'Response Code':500,'Response Message':'Unsuccessful','Response Data':[]})

def pushBulk(lst,pid,spid):
    matchstr =[]
    for i in lst:
            dic = {}
            df = search_by_tfidf(pid,i,spid,db="bulkstringdb")
            if df['Response Message'] == "Insertion Success":
                continue
            elif df['Response Message'] in ["Could not Insert","Project Does not exist","Sub project does not exist","Unexpected Error."]:
                return -1
            else:
                dic['string']= i
                dic['matched'] = df['Response Data']
            matchstr.append(dic)
    return matchstr

def pushsub(pid,spid):
    strings = MongoClient(dbURL).stringdb['projectmap']
    try:
        x = MongoClient(dbURL).stringdb[pid]
        lst = []
        for i in strings.find({pid:{'$exists':'true'}}):
            lst.append(i[pid])
        if spid.capitalize() not in lst:
            x=strings.insert({pid:spid.capitalize()})
            if(type(x).__name__ == "ObjectId"):
                return 1
            else:
                return 0
        else:
            return 2
    except:
        return 0

def ret_exists(pid):
    if pid in ret_collection():
        return True
    else:
        return False

def ret_collection():
    c_names = MongoClient(dbURL).stringdb.collection_names()
    return c_names

def ret_subprojects(pid):
    if ret_exists(pid):
        lst = []
        for i in MongoClient(dbURL).stringdb['projectmap'].find({pid:{'$exists':'true'}}):
            lst.append(i[pid])
        return lst
    else:
        return False

def make_collection(pid):
    try:
        bulkstrings = MongoClient(dbURL).bulkstringdb.create_collection(pid.capitalize())
        strings = MongoClient(dbURL).stringdb.create_collection(pid.capitalize())
        if type(strings).__name__ == "Collection":
            return True
        else:
            return "Unexpected"
    except:
        return False

def insert(pid,arg,spid,db):
    if db == "stringdb":
        strings = MongoClient(dbURL).stringdb[pid]
    elif db == "bulkstringdb":
        strings = MongoClient(dbURL).bulkstringdb[pid]
    if ret_exists(pid):
        if spid in ret_subprojects(pid):
            try:
                x=strings.insert({'spid':spid,'string':arg})
                if(type(x).__name__ == "ObjectId"):
                    return 1
                else:
                    return 0
            except:
                return 0
        else:
            return 3
    else:
        return 2



def search_by_tfidf(pid,arg,spid,db = "stringdb"):
    docs=[]
    docs_original=[]
    docs.append(arg)
    docs_original.append(arg)
    if db == "stringdb":
        strings = MongoClient(dbURL).stringdb[pid]
    elif db == "bulkstringdb":
        strings = MongoClient(dbURL).bulkstringdb[pid]
    for i in strings.find({'string':{'$exists':'true'},'spid':spid}):
        docs_original.append(i['string'])
        docs.append(_prettify_string(i['string'].lower()))
    instance = TfidfVectorizer()
    matrix = instance.fit_transform(docs)
    cosine_matrix = cs(matrix[0:1],matrix)[0]
    retval={'Response Code':200,'Response Message':'Success','Response Data':[]}
    for i in range(1,len(cosine_matrix)):
        if (len(arg)<len(docs_original[i])) and (arg in docs_original[i]):
            retval['Response Data'].append({'stri':docs_original[i],'perc':str(100)})
        elif(cosine_matrix[i]*100 > 60):
            retval['Response Data'].append({'stri':docs_original[i],'perc':str(cosine_matrix[i]*100)})
        else:
            pass
    if retval['Response Data'] != []:
        return retval
    else:
        print("Inserting...")
        ret=insert(pid,arg,spid,db)
        if ret==0:
            return {"Response Code":"501","Response Message":"Could not Insert"}
        elif ret == 1:
            return {"Response Code":"200","Response Message":"Insertion Success"}
        elif ret == 2:
            return {"Response Code":"403","Response Message":"Project Does not exist"}
        elif ret ==3 :
            return {"Response Code":"403","Response Message":"Sub project does not exist"}
        else:
            return {"Response Code":"500","Response Message":"Unexpected Error."}
def search(pid,arg,spid,db = "strigdb"):
    arg=_prettify_string(arg.lower())
    if db=="stringdb":
        strings =  MongoClient().stringdb[pid]
    elif db == "bulkstringdb":
        strings = MOngoClient().bulkstringdb[pid]
    cursor = strings.find({'spid':spid})
    retval=[]
    for i in cursor:
        if (_match_str(_prettify_string(i['string'].lower()),arg)>30):
             retval.append(i['string'])
    if retval==[]:
        ret = insert(pid,arg,spid,db)
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
