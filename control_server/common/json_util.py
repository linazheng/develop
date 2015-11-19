# encoding: utf8
import json




def toJSONString(obj, encoding="utf8", indent=None):
    if indent==None:
        return json.dumps(obj).encode(encoding);
    else:
        return json.dumps(obj, indent=indent).encode(encoding);


def parseToJson(jsonStr):
    return json.loads(jsonStr)

