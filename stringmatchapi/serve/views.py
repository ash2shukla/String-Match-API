# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from .strmatch import search_by_tfidf,ret_collection,ret_exists,insert,make_collection
from json import dumps

def indexview(request):
    pid = request.GET.get('pid')
    if pid =="":
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    if not ret_exists(pid):
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Does Not Exist"}))
    query = request.GET.get('query')
    if query=="":
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Query Should Not Be Null"})) 
    try:
        start=int(request.GET.get('start'))
    except :
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Give Start"}))
    try:
        end=int(request.GET.get('end'))
    except :
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Give End"}))
    retval = search_by_tfidf(pid,query)
    try:
        retval['Response Data']=retval['Response Data'][start:end]
        return HttpResponse(dumps(retval))
    except KeyError:
        return HttpResponse(dumps(retval))
    except:
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
        
def no_objection(request):
    pid = request.GET.get('pid')
    if pid =="":
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Should Not be Null"}))
    if not ret_exists(pid):
        return HttpResponse(dumps({"Reponse Code":"403","Response Message":"Bad Request. Project Does Not Exist"}))
    query = request.GET.get('query')
    if query=="":
        return HttpResponse(dumps({"Response Code":"403","Response Message":"Bad Request. Query Should Not Be Null"})) 
    retval = insert(pid,query)
    if retval ==1 :
        return HttpResponse(dumps({"Response Code":"200","Response Message":"Insertion Success"}))
    elif retval == 0 :
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
       
def collectionview(request):
    return HttpResponse(dumps({"projects":ret_collection()}))

def collectioninsert(request):
    c_name = request.GET.get('pid')
    if c_name == "":
        return HttpReponse(dumps({"Response Code":"403","Response Message":"Bad Request. PID Should Not Be Null"}))
    retval=make_collection(c_name)
    if retval == "Unexpected":
        return HttpResponse(dumps({"Response Code":"500","Response Message":"Unexpected Error"}))
    elif retval == True:
        return HttpResponse(dumps({"Response Code":"200","Response Message":"Project Creation Success"}))
    elif retval == False:
        return HttpResponse(dumps({"Response Code":"501","Response Message":"Could not Insert"}))
    
