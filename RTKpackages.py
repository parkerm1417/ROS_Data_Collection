from os import listdir,system,remove
import subprocess
import time
import json
from services import serviceFunc
from messages import messageFunc
from datetime import date

start = time.time()
primitives = ["byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]"]

########################################
##Ensures that a new roscore is running
########################################
system("killall -9 rosmaster")
try:
    subprocess.Popen("roscore")
    time.sleep(2.5)
except:
    pass

system("rospack list > ~/Desktop/packageslist.txt")
packs = open("packageslist.txt")
packslist = packs.readlines()
packs.close()

allpacks = {}

packs = open("packageslist.txt","w")
for pack in packslist:
    sp = pack.find(" ")
    packs.write(pack[:sp] + "\n")
    allpacks[pack[:sp]] = pack[sp+1:]
packs.close()
packs = open("packageslist.txt")
packslist = packs.readlines()
packs.close()
for pl in range(len(packslist)):
    packslist[pl] = packslist[pl][:-1]
print("Packages list updated, please see 'packageslist.txt' on Desktop for full list\n")

try:
    file = open("PreviousRun.json")
    prev = file.read()
    prevfile = json.loads(prev)
    file.close()
    SavedRun = prevfile
    Complete = prevfile["Complete"]
    alreadydoneMSGS = prevfile["alreadydoneMSGS"]
    alreadydoneSERV = prevfile["alreadydoneSERV"]
    messagescheck = prevfile["messagescheck"]
    servicescheck = prevfile["servicescheck"]
    Topics = prevfile["Topics"]
    packages = prevfile["packages"]
    inputName = prevfile["inputName"]

    print("Previous run found!")
    continueRun = input("Would you like to continue this previous run? (Y/n): ")
    print("")
    
except:
    Complete = {}
    Topics = {}
    alreadydoneMSGS = []
    alreadydoneSERV = []
    
    continueRun = "N"
    
    print("No previous run found, new files created\n")
    
distro = subprocess.getoutput("rosversion -d")
try:
    if distro != Complete["Distribution"]:
        Complete = {}
        Topics = {}
        alreadydoneMSGS = []
        alreadydoneSERV = []
        print("Distribution has changed since last run, new files must be created")
except:
    pass

#######################################################################################################
#######################################################################################################
if(continueRun == "n" or continueRun == "N"):

    SavedRun = {"Complete" : {},
                "alreadydoneMSGS" : [],
                "alreadydoneSERV" : [],
                "Topics" : {},
                "packages" : [],
                "inputName" : "",
                "date" : "",
                "messagescheck" : False,
                "servicescheck" : False}
    Complete = {}
    Topics = {}
    alreadydoneMSGS = []
    alreadydoneSERV = []
    packages = []
    messagescheck = False
    servicescheck = False

    while ((not set(packages).issubset(set(packslist))) or (packages == [])):
        if packages != []:
            print("*****One or more packages is not a valid entry. Please check your packages and try again.*****\n")
        try:
            remove("tempMessages.json")
        except:
            pass

        try:
            remove("tempServices.json")
        except:
            pass
        
        packstorun = input("Please list desired packages and seperate multiple packages with a comma (NO SPACES)\nYou will find all available packages in packageslist.txt\nThe package names are everything prior to the space on each line\nIf you would like all packages to run, please type \"ALL\"\nPackages: ")
        print("")

        if(packstorun == "ALL"):
            packages = [f for f in allpacks]
            packages.sort()
                
        elif(packstorun[-4:] == ".txt"):
            file = open(packstorun)
            packages = file.readlines()
            file.close()
            
        else:
            packages = [x for x in packstorun.split(",")]

    SavedRun["packages"] = packages    
    inputName = input("what would you like to name the outputted files?\nFile names will be of the format:\n'YOUR INPUT'_msgs_Date.json\nFile Name: ")
    SavedRun["inputName"] = inputName

    file = open("PreviousRun.json","w")
    file.write(json.dumps(SavedRun))
    file.close()
          
print("")
if not messagescheck:
    messageFunc(packages,distro,inputName)
    SavedRun["messagescheck"] = True
    file = open("PreviousRun.json","w")
    file.write(json.dumps(SavedRun))
    file.close()
    print("")
if not servicescheck:
    serviceFunc(packages,distro,inputName)
    SavedRun["servicescheck"] = True
    file = open("PreviousRun.json","w")
    file.write(json.dumps(SavedRun))
    file.close()
    print("")

Complete["Distribution"] = distro

Topics["Distribution"] = distro
today = date.today()
Complete["Date"] = today.strftime("%x")

Topics["Date"] = today.strftime("%x")

SavedRun["date"] = today.strftime("%x")

for pack in range(len(packages)):
    if packages[pack] not in Complete:
        Complete[packages[pack]] = {    ##creates a dictionary for each package that then holds a node dictionary
        "elementType" : "package",
        "name" : packages[pack],
        "distribution" : "",
        "nodes" : {},
        "messages" : {},
        "services" : {}
        }

        temp = []
        try:
            temp = [f for f in listdir('/opt/ros/'+distro+'/lib/' + packages[pack])]  ##each package directory is accessed
            Complete[packages[pack]]["distribution"] = "ROS/"+distro
        except:
            pass
        
        try:
            temp = [f for f in listdir('/opt/rtk/'+distro+'/lib/' + packages[pack])]
            Complete[packages[pack]]["distribution"] = "RTK/"+distro
        except:
            pass

        system("rosnode list > temptext.txt")
        file = open("temptext.txt")
        oldlines = file.readlines()
        file.close()

        for node in temp:

                Complete[packages[pack]]["nodes"][node] = {
                "elementType" : "node",
                "name" : node,
                "publications": {},
                "subscriptions": {},
                "services provided": {},
                "services used": {}
                }

                run = "rosrun " + packages[pack] + " " + node     ##runs each node in the terminal and renames the node to be exact when being terminated 
                kill = "killall " + node       ##kills all active nodes

                runner = subprocess.Popen(run,shell=True)
                time.sleep(1)

                system("rosnode list > temptext.txt")
                file = open("temptext.txt")
                newlines = file.readlines()
                file.close
                for new in newlines:
                    if (new not in oldlines):
                        CurrentNode = new[:-1]
                        break
                    else:
                        CurrentNode = ""

                rnode = "rosnode info -q " + CurrentNode + " > temptext.txt"       ##gets info about each nod and puts it into a .txt file to be accessed later
                noder = subprocess.Popen(rnode,shell=True)
                time.sleep(1)


                file = open("temptext.txt")
                lines = file.readlines()       ##reads all of the text within the file and sets it equal to a variable
                file.close()
                pub = 0
                sub = 0
                serv = 0

                ##Looks at the fourth letter of each line to determine whether the information is about a publication, subscription, or service
                for n in range(len(lines)):
                    if (lines[n] != "\n"):
                        if (lines[n][3] == "l"):
                            pub = n
                        elif(lines[n][3] == "s"):
                            sub = n
                        elif (lines[n][3] == "v"):
                            serv = n

                pubtemp=[]
                subtemp=[]
                servtemp=[]
                nodeinfotemp = []

                ##adds the publication, subscription, and service info to temporary lists
                for n in range(len(lines)):
                    if (n>pub and n<sub-1):
                        ss = lines[n][3:-1]
                        f = ss.find("[")
                        toptype = ss[f+1:-1]
                        q = ss.find("/",1,f-1)
                        if(q == -1):
                            title = ss[1:f-1]
                        else:
                            title = ss[q+1:f-1]
                        Complete[packages[pack]]["nodes"][node]["publications"][title] = {
                            "elementType" : "topic",
                            "name" : title,
                            "type" : toptype }
                        ob = ss.find("[")      ##for formatting purposes, extraneous symbols are removed
                        bs = ss.find("/", 1, ob)
                        topicname = ss[:ob-1]
                        datatype = ss[ob+1:-1]
                        try:        ##checks to see if the topic has already been filled with its information, and if so, only adds on the publisher/subscriber info
                            Topics[topicname]["publishers"][node] = {
                                "elementType": "node",
                                "name": node,
                                "package": pack
                                }
                        except:     ##adds a dictionary to each topic and fills it with information, each publisher and subscriber is also assigned an empty dictionary
                            Topics[topicname] = {
                            "elementType": "topic",
                            "name": topicname,
                            "type": "",
                            "data": "TBD",
                            "publishers": {node:{
                                "elementType": "node",
                                "name": node,
                                "package": pack}},
                            "subscribers": {}
                            }
                        if(datatype != "unknown type" and Topics[topicname]["type"] == ""):     
                            Topics[topicname]["type"] = datatype

                    elif (n>sub and n<serv-1):
                        ss = lines[n][3:-1]
                        f = ss.find("[")
                        toptype = ss[f+1:-1]
                        q = ss.find("/",1,f-1)
                        title = ss[:f-1]
                        subtype = subprocess.getoutput("rostopic info "+title)
                        endline = subtype.find("\n")
                        Type = subtype[6:endline]
                        Complete[packages[pack]]["nodes"][node]["subscriptions"][title[1:]] = {
                            "elementType" : "topic",
                            "name" : title[1:],
                            "type" : Type
                            }
                        ob = ss.find("[")      ##for formatting purposes, extraneous symbols are removed
                        bs = ss.find("/", 1, ob-1)
                        topicname = ss[:ob-1]
                        try:        ##checks to see if the topic has already been filled with its information, and if so, only adds on the publisher/subscriber info
                            Topics[topicname]["publishers"][node] = {
                                "elementType": "node",
                                "name": node,
                                "package": pack
                                }
                        except:     ##adds a dictionary to each topic and fills it with information, each publisher and subscriber is also assigned an empty dictionary
                            Topics[topicname] = {
                            "elementType": "topic",
                            "name": topicname,
                            "type": "",
                            "data": "TBD",
                            "publishers": {},
                            "subscribers": {node:{
                                "elementType": "node",
                                "name": node,
                                "package": pack}},
                            }
                        if(Type != "unknown type" and Topics[topicname]["type"] == ""):     
                            Topics[topicname]["type"] = Type

                    elif (n>serv and n<len(lines)-1):
                        servtemp.append(lines[n][3:-1])

                for servs in servtemp:
                    args = subprocess.getoutput("rosservice args "+servs)
                    servtype = subprocess.getoutput("rosservice type "+servs)
                    q = servs.find("/",1)
                    if(q == -1):
                        title = servs[1:]
                    else:
                        title = servs[q+1:]

                    Complete[packages[pack]]["nodes"][node]["services provided"][title] = {
                    "elementType" : "service",
                    "name" : servs,
                    "type" : servtype,
                    "args" : args}

                killname = "rosnode kill -a"
                killer = subprocess.Popen(killname,shell=True)
                kill2 = subprocess.Popen(kill,shell=True)
                time.sleep(1)

                system("rosnode list > temptext.txt")
                file = open("temptext.txt")
                oldlines = file.readlines()
                file.close

                runner.terminate()
                noder.terminate()
                killer.terminate()
                kill2.terminate()

        SavedRun["Complete"] = Complete
        SavedRun["Topics"] = Topics
        file = open("PreviousRun.json","w")
        file.write(json.dumps(SavedRun))
        file.close()

        print("Package "+ str(pack+1) +" of "+ str(len(packages)) + " complete")
        system("rosnode kill -a")
system("rosnode kill -a")
print("PACKAGES COMPLETED\n")

########################################################################################
########################################################################################

system("rosmsg list > temptext.txt")
msgfile = open("temptext.txt")
msglistlines = msgfile.readlines()
msgfile.close()
##fills the messages dictionary
edits = []
for msg in msglistlines:
    bs = msg.find("/")
    package = msg[:bs]
    if package in packages:
        edits.append(msg)
        
for msg in range(len(edits)):
    if edits[msg] not in alreadydoneMSGS:
        bs = edits[msg].find("/")
        package = edits[msg][:bs]
        file = edits[msg][bs+1:-1] + ".msg"
        system("rosmsg info " + edits[msg][:-1] + " > temptext.txt")
        Complete[package]["messages"][edits[msg][:-1]] = {"name": edits[msg][:-1],
                                                                 "elementType": "message",
                                                                 "fields": {}}
        try:
            com = open("/opt/ros/" + distro + "/share/" + package + "/msg/" + file)
        except:
            com = open("/opt/rtk/" + distro + "/share/" + package + "/msg/" + file)
        comments = com.readlines()
        com.close()


        msginfo = open("temptext.txt")
        msginfolines = msginfo.readlines()
        msginfo.close()
        for x in range(len(msginfolines)-1):
            p = 0
            while msginfolines[x][p] == " ":
                p += 1
            midsp = msginfolines[x].find(" ", p)
            msgtype = msginfolines[x][p : midsp]
            msgname = msginfolines[x][midsp + 1:-1]

            if p == 0:
                lvl1 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}

                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}

            elif p == 2:
                lvl2 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 4:
                lvl3 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 6:
                lvl4 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 8:
                lvl5 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 10:
                lvl6 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 12:
                lvl7 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6]["fields"][lvl7] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6]["fields"][lvl7] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}
            elif p == 14:
                lvl8 = msgname
                if (msgtype in primitives):
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6]["fields"][lvl7]["fields"][lvl8] = {
                        "name": msgname,
                        "elementType": "dataType",
                        "storageType": msgtype,
                        "dmfDataType":"TBD"}
                else:
                    Complete[package]["messages"][edits[msg][:-1]]["fields"][lvl1]["fields"][lvl2]["fields"][lvl3]["fields"][lvl4]["fields"][lvl5]["fields"][lvl6]["fields"][lvl7]["fields"][lvl8] = {
                        "name": msgname,
                        "elementType": "messageType",
                        "type": msgtype,
                        "dmfDataType":"TBD",
                        "fields":{}}

        alreadydoneMSGS.append(edits[msg])
        SavedRun["alreadydoneMSGS"] = alreadydoneMSGS
          
        file = open("PreviousRun.json","w")
        file.write(json.dumps(SavedRun))
        file.close()

        print("Message "+ str(msg+1) +" of "+ str(len(edits)) + " complete")
print("MESSAGES COMPLETED\n")

##############################################################################################
##############################################################################################

system("rossrv list > temptext.txt")
s = open("temptext.txt")
srvlist = s.readlines()
s.close()

edits = []
for srv in srvlist:
    bs = srv.find("/")
    package = srv[:bs]
    if package in packages:
        edits.append(srv)    

for srv in edits:
    if srv not in alreadydoneSERV:
        bs = srv.find("/")
        package = srv[:bs]
        try:
            qwe = Services[srv[bs+1:-1]]["requestMessage"]
            continue
        except:
            pass
        
        file = srv[bs+1:-1] + ".srv"
        try:
            com = open("/opt/ros/" + distro + "/share/" + package + "/srv/" + file)
        except:
            com = open("/opt/rtk/" + distro + "/share/" + package + "/srv/" + file)
        comments = com.readlines()
        try:
            try:
                comsplit = comments.index("---\n")
            except:
                comsplit = comments.index("---")
        except:
            comsplit = len(comments)
        com.close()
        cmd = "rossrv info "+srv[:-1]+" > temptext.txt"
        system(cmd)
        s = open("temptext.txt")
        srvinfo = s.readlines()
        s.close()
        split = srvinfo.index("---\n")
        bs = srv.find("/")
        pack = srv[:bs]
        args = subprocess.getoutput("rosservice args "+srv)
        Complete[pack]["services"][srv[:-1]]= {
                        "name":srv[:-1],
                        "elementType": "service",
                        "requestMessage": srv[:-1]+"Request",
                        "responseMessage": srv[:-1]+"Response"}
        Complete[pack]["messages"][srv[:-1]+"Request"] = {"name": srv[:-1]+"Request",
                                        "elementType": "message",
                                        "fields": {}}
        Complete[pack]["messages"][srv[:-1]+"Response"] = {"name": srv[:-1]+"Response",
                                         "elementType": "message",
                                         "fields": {}}

        for msg in range(len(srvinfo)-1):
            sp = 0
            for ch in srvinfo[msg]:
                if( ch == " "):
                    sp += 1
                else:
                    break

            nmsp = srvinfo[msg].find(" ",sp)
            msgtype = srvinfo[msg][sp:nmsp]
            msgname = srvinfo[msg][nmsp+1:-1]

            if msg > split:

                if sp == 0:
                    lv1 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}

                elif sp == 2:
                    lv2 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 4:
                    lv3 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 6:
                    lv4 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 8:
                    lv5 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 10:
                    lv6 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 12:
                    lv7 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 14:
                    lv8 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7]["fields"][lv8] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Response"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7]["fields"][lv8] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}

            elif msg < split:

                if sp == 0:
                    lv1 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}

                elif sp == 2:
                    lv2 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 4:
                    lv3 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 6:
                    lv4 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 8:
                    lv5 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 10:
                    lv6 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 12:
                    lv7 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}
                elif sp == 14:
                    lv8 = msgname
                    if (msgtype in primitives):
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7]["fields"][lv8] = {
                            "name":msgname,
                            "elementType": "dataType",
                            "storageType": msgtype,
                            "dmfDataType":"TBD"}
                    else:
                        Complete[pack]["messages"][srv[:-1]+"Request"]["fields"][lv1]["fields"][lv2]["fields"][lv3]["fields"][lv4]["fields"][lv5]["fields"][lv6]["fields"][lv7]["fields"][lv8] = {
                            "name": msgname,
                            "elementType": "messageType",
                            "type": msgtype,
                            "dmfDataType":"TBD",
                            "fields":{}}

        alreadydoneSERV.append(srv)
        SavedRun["alreadydoneSERV"] = alreadydoneSERV
        
        file = open("PreviousRun.json","w")
        file.write(json.dumps(SavedRun))
        file.close()

        print("Service "+ str(edits.index(srv)+1) +" of "+ str(len(edits)) + " complete")
print("SERVICES COMPLETED\n")

###############################################################################################
###############################################################################################


top = open(inputName + "_TopicsDictionary_" + ".json", "w")
top.write(json.dumps(Topics, indent=8))
top.close()

comp = open(inputName + "_PackageDictionary_" + date.today().strftime("%m_%d_%Y") + ".json", "w")
comp.write(json.dumps(Complete, indent=8))
comp.close()

remove("PreviousRun.json")

print("total time elapsed: " + str(time.time()-start) + " seconds\n")
system("killall -9 rosmaster")

while(True):
    print("PROGRAM IS DONE RUNNING PLEASE KILL ANY PROGRAMS STILL RUNNING")
    time.sleep(0.1)