# encoding: utf8
import types
from operator import isMappingType
import datetime
from logging import Logger


def put(varDict, key, value):
    varDict[key] = value


def get(varDict, key, defValue=None):
    if varDict.has_key(key):
        return varDict[key]
    return defValue


def removeKey(varDict, key):
    if varDict.has_key(key):
        del(varDict[key])
        

        
# transform a obj into a Dictionary data
# deep
def toDictionary(obj, max_deep=3, cur_deep=1):
#     print("toDictionary()", type(obj), obj)
    
    if obj==None:
        return obj;
    
    elif isinstance(obj, int):
        return obj;
    
    elif isinstance(obj, long):
        return obj;
    
    elif isinstance(obj, float):
        return obj;
    
    elif isinstance(obj, bool):
        return obj;
    
    elif isinstance(obj, str):
        return obj;
    
    elif isinstance(obj, datetime.datetime):
        return str(obj);
    
    elif isinstance(obj, Logger):
        return "logger [%s] of %s" % (obj.name, str(obj));
    
    elif type(obj)==types.TypeType:
        return str(obj);
    
    elif callable(obj):
        return str(obj)
    
    else:
        
        if cur_deep > max_deep:
            return "<--(%s)(reach max deep: %s)-->" % (obj, max_deep)
         
        cur_deep += 1

        if isMappingType(obj):
            # dict || OrderedDict
            _rt = {}
            for _p in obj:
                _rt[_p] = toDictionary(obj[_p], max_deep=max_deep, cur_deep=cur_deep)
            return _rt;
        
        else:
            # list || set
            try:
                iter(obj)   # if iterable
                _rt = []
                for _p in obj:
                    _rt.append(toDictionary(_p, max_deep=max_deep, cur_deep=cur_deep))
                return _rt;
            except:
                pass
            # every type of class
            _rt = {"__type__":str(obj)}
            for _p in dir(obj):
                if type(_p)==types.StringType and _p.startswith("__"):
                    continue
                _value = getattr(obj, _p)
                if callable(_value):
                    continue
                _rt[_p] = toDictionary(_value, max_deep=max_deep, cur_deep=cur_deep)
            return _rt;
                
    
    
#--------------------

# _dict = {
#          "a" : "1a",
#          "b" : {
#              "a" : "2a",
#              "b" : {
#                  "a" : "3a",
#                  "b" : {
#                      "a" : "4a",
#                      "b" : {
#                          "a" : "5a",
#                          "b" : "5b"
#                          }
#                      }
#                  }
#              }
#          }
# 
# 
# print toDictionary(_dict) 
        
        
        
        
        
        
        