from os import listdir,system,remove
import subprocess
import time
import json
from datetime import date

################################################################################
##This function gets all of the services that are provided by the packages in
##the complete dictionary and then adds those services to a separate dictionary
##of its own. This dictionary holds all of the services for the packages that
##were asked for by the user. This function is called in RTKpackages.py.
################################################################################
def serviceFunc(packages,distro,inputName,Complete):
    primitives = ["byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]"]

    edits = []

    try:
        file = open("tempServices.json")
        prev = file.read()
        msgdic = json.loads(prev)
    except:
        msgdic = {}

##Gets the services provided from the packages in the complete dictionary and stores it in a list "edits"
    for pack in Complete:
        if pack != "Distribution" and pack != "Date":
            for node in Complete[pack]["nodes"]:
                for serv in Complete[pack]["nodes"][node]["services provided"]:
                    if Complete[pack]["nodes"][node]["services provided"][serv]["type"] not in edits:
                        edits.append(Complete[pack]["nodes"][node]["services provided"][serv]["type"])
    c=1

##If the service is not already in the dictionary, then the service gets added. This ensures that the
##same service isn't added more than once.
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
            ##Adds on to a temporary dictionary to ensure that if the code crashes or is stopped
            ##that the information will be saved and the code will be able to pick up where it left off
            file = open("tempServices.json","w")
            file.write(json.dumps(msgdic))
            file.close()
            
        c+=1
##Creates a file using the user input as a part of the name, as well as the date.
##This file gets added to the current directory of the user.        
    filename =  inputName + "_srvs_" + date.today().strftime("%m_%d_%Y") + ".json"
    srvs = open(filename,"w")
    srvs.write(json.dumps(msgdic, indent = 8))
    srvs.close()
    remove("tempServices.json")
    return

