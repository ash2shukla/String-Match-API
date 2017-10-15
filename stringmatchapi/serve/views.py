# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from .strmatch import getFile,ret_subprojects,search_by_tfidf,ret_collection,ret_exists,insert,make_collection,pushsub
from json import dumps

def bulkview(request):
    url = request.GET.get('url')
    pid = request.GET.get('pid')
    spid = request.GET.get('spid')
    if url =="" or url is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. URL Should Not be Null"}))
    if pid =="" or pid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    if spid =="" or spid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. SubProject Should Not be Null"}))
    retval = getFile(url,pid,spid,True)
    return HttpResponse(retval,content_type="application/json")

def bulkinsert(request):
    url = request.GET.get('url')
    pid = request.GET.get('pid')
    spid = request.GET.get('spid')
    if url =="" or url is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. URL Should Not be Null"}))
    if pid =="" or pid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    if spid =="" or spid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. SubProject Should Not be Null"}))
    retval = getFile(url,pid,spid,False)
    return HttpResponse(retval,content_type="application/json")

def indexview(request):
    pid = request.GET.get('pid')
    spid = request.GET.get('spid')
    if pid =="" or pid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    if not ret_exists(pid):
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Does Not Exist"}))
    query = request.GET.get('query')
    if spid=="" or spid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Sub Project Should Not be Null"}))
    if spid not in ret_subprojects(pid):
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Sub Projects doesn't exist."}))
    if query=="" or query is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Query Should Not Be Null"}))
    try:
        start=int(request.GET.get('start'))
    except :
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Give Start"}))
    try:
        end=int(request.GET.get('end'))
    except :
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Give End"}))
    retval = search_by_tfidf(pid,query,spid)
    try:
        retval['Response Data']=retval['Response Data'][start:end]
        return HttpResponse(dumps(retval))
    except KeyError:
        return HttpResponse(dumps(retval))
    except:
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))

def no_objection(request):
    pid = request.GET.get('pid')
    if pid =="" or pid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    spid = request.GET.get('spid')
    if spid == "" or spid is None:
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Sub Project Should Not be Null"}))
    if not ret_exists(pid):
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Does Not Exist"}))
    query = request.GET.get('query')
    if query=="" or query is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Query Should Not Be Null"}))
    retval = insert(pid,query,spid)
    if retval ==1 :
        return HttpResponse(dumps({"Response Code":"200","Response Message":"Insertion Success"}))
    elif retval == 0 :
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
    elif retval == 2 :
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Project doesn't exist"}))
    elif retval == 3 :
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Sub Project doesn't exist"}))

def collectionview(request):
    return HttpResponse(dumps({"projects":ret_collection()}))

def subprojectview(request):
    pid = request.GET.get('pid')
    if pid == "" or pid is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. PID Should Not Be Null"}))
    else:
        retval = ret_subprojects(pid)
        if isinstance(retval,list):
            return HttpResponse(dumps({"subproject":retval}))
        else:
            return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. PID doesn't exist."}))

def collectioninsert(request):
    c_name = request.GET.get('pid')
    if c_name == "" or c_name is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. PID Should Not Be Null"}))
    retval=make_collection(c_name)
    if retval == "Unexpected":
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
    elif retval == True:
        return HttpResponse(dumps({"Response Code":"200","Response Message":"Project Creation Success"}))
    elif retval == False:
        return HttpResponse(dumps({"Response Code":"501","Response Message":"Could not Insert"}))


def mapprojects(request):
    c_name = request.GET.get('pid')
    sub_name = request.GET.get('spid')
    if c_name == "" or c_name is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. PID Should Not Be Null"}))
    if sub_name == "" or sub_name is None:
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. SPID Should Not Be Null"}))
    if ret_exists(c_name):
        retval= pushsub(c_name,sub_name)
        if retval==1:
            return HttpResponse(dumps({"Response Code":"200","Response Message":"Subproject Inserted"}))
        elif retval == 2:
            return HttpResponse(dumps({"Response Code":"200","Response Message":"Subproject Already exists"}))
        else:
            return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
    else:
            return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Project doesn't exist."}))
