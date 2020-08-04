from os import listdir,system,remove
import subprocess
import time
import json
from datetime import date


def serviceFunc(packages,distro,inputName):
    primitives = ["byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]"]

    ##msglist = input("Please type all services you would like information on. Separate services with commas.\nServices:")
    ##if msglist == "ALL":
    ##    file = subprocess.getoutput("rossrv list")
    ##    messages = file.split("\n")
    ##else:
    ##    messages = [x for x in msglist.split(",")]

    file = subprocess.getoutput("rossrv list")
    messages = file.split("\n")
    edits = []

    for message in messages:
            bs = message.find("/")
            if message[:bs] in packages:
                edits.append(message)

    try:
        file = open("tempServices.json")
        prev = file.read()
        msgdic = json.loads(prev)
    except:
        msgdic = {}

    c=1
    
    for msg in edits:
        if msg not in msgdic:
            bs = msg.find("/")
            msgdic[msg] = {
                "name": msg[bs+1:],
                "elementType": "service",
                "requestMessage": msg[bs+1:]+"Request",
                "responseMessage": msg[bs+1:]+"Response"
                }
            print("Service "+ str(c) +" of "+ str(len(edits)) +" completed")

            file = open("tempServices.json","w")
            file.write(json.dumps(msgdic))
            file.close()
            
        c+=1

    msgitems = msgdic.items()
    msgdic = sorted(msgitems)

    filename =  inputName + "_srvs_" + date.today().strftime("%m_%d_%Y") + ".json"
    srvs = open(filename,"w")
    srvs.write(json.dumps(msgdic, indent = 8))
    srvs.close()
    remove("tempServices.json")
    return
