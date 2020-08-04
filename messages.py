from os import listdir,system,remove
import subprocess
import time
import json
from datetime import date


def messageFunc(packages,distro,inputName):
    primitives = ["char","byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]"]

    file = subprocess.getoutput("rosmsg list")
    messages = file.split("\n")
    file = subprocess.getoutput("rossrv list")
    servs = file.split("\n")
    for srv in servs:
        messages.append(srv+"Request")
        messages.append(srv+"Response")
    edits = []
    for message in messages:
        bs = message.find("/")
        if message[:bs] in packages:
            edits.append(message)
    tempdic = {"msgdic" : {}, "edits" : []}
    try:
        file = open("tempMessages.json")
        prev = file.read()
        previous = json.loads(prev)
        msgdic = previous["msgdic"]
        edits = previous["edits"]
    except:
        msgdic = {}

    p = 1
    
    for msg in edits:
        if msg not in msgdic:
            Done = False
            bs = msg.find("/")
            msgdic[msg] = {
                "package" : msg[:bs],
                "distribution" : "",
                "fields": {},
                "comments": {}
                }
            if(msg[-7:] == "Request"):
                try:
                    system("rossrv info "+msg[:-7]+" > temptext.txt")
                    file = open("temptext.txt")
                    msginfo = file.readlines()
                    file.close()
                    try:
                        split = msginfo.index("---\n")
                        
                    except:
                        split = msginfo.index("---")
                    for line in range(split+1,len(msginfo)):
                        if(msginfo[line][0] != " " and msginfo[line] != "\n"):
                            sp = msginfo[line].find(" ")
                            msgdic[msg]["fields"][msginfo[line][sp+1:-1]] = msginfo[line][:sp]
                            if ((msginfo[line][:sp] not in primitives) and (msginfo[line][:sp] not in edits)):
                                if(msginfo[line][:sp][-1] == "]"):
                                    q = msginfo[line][:sp]
                                    br = q.find("[")
                                    q = q[:br]
                                    if (q not in messages) and (q not in primitives):
                                        edits.append(q)
                                else:
                                    edits.append(msginfo[line][:sp])
                    bs = msg.find("/")
                    try:
                        file = open("/opt/ros/"+distro+"/share/"+msg[:bs]+"/srv/"+msg[bs+1:-7]+".srv")
                        msgdic[msg]["distribution"] = "ROS/" + distro
                    except:
                        file = open("/opt/rtk/"+distro+"/share/"+msg[:bs]+"/srv/"+msg[bs+1:-7]+".srv")
                        msgdic[msg]["distribution"] = "RTK/" + distro

                    comments = file.readlines()
                    file.close()
                    c = 1
                    try:
                        try:
                            split = comments.index("---\n")
                        except:
                            split = comments.index("---")
                    except:
                        split = len(comments)
                    for com in range(split):
                        while comments[com][0] == " ":
                            comments[com] = comments[com][1:]
                        if(comments[com][-1] == "\n"):
                            msgdic[msg]["comments"][c] = comments[com][:-1]
                        else:
                            msgdic[msg]["comments"][c] = comments[com]
                        c += 1
                    Done = True
                except:
                    pass
                
            elif(msg[-8:] == "Response"):
                try:
                    system("rossrv info "+msg[:-8]+" > temptext.txt")
                    file = open("temptext.txt")
                    msginfo = file.readlines()
                    file.close()
                    
                    try:
                        split = msginfo.index("---\n")
                    except:
                        split = msginfo.index("---")
                    
                    for line in range(split+1,len(msginfo)):
                        if(msginfo[line][0] != " " and msginfo[line] != "\n"):
                            sp = msginfo[line].find(" ")
                            msgdic[msg]["fields"][msginfo[line][sp+1:-1]] = msginfo[line][:sp]
                            if ((msginfo[line][:sp] not in primitives) and (msginfo[line][:sp] not in edits)):
                                if(msginfo[line][:sp][-1] == "]"):
                                    q = msginfo[line][:sp]
                                    br = q.find("[")
                                    q = q[:br]
                                    if (q not in messages) and (q not in primitives):
                                        edits.append(q)
                                else:
                                    edits.append(msginfo[line][:sp])
                    bs = msg.find("/")
                    try:
                        file = open("/opt/ros/"+distro+"/share/"+msg[:bs]+"/srv/"+msg[bs+1:-8]+".srv")
                        msgdic[msg]["distribution"] = "ROS/" + distro
                    except:
                        file = open("/opt/rtk/"+distro+"/share/"+msg[:bs]+"/srv/"+msg[bs+1:-8]+".srv")
                        msgdic[msg]["distribution"] = "RTK/" + distro
                        
                    comments = file.readlines()
                    file.close()
                    c = 1

                    try:
                        try:
                            split = comments.index("---\n")
                        except:
                            split = comments.index("---")
                    except:
                        split = len(comments)
                        
                    for com in range(split+1,len(comments)):
                        while comments[com][0] == " ":
                            comments[com] = comments[com][1:]
                        if(comments[com][-1] == "\n"):
                            msgdic[msg]["comments"][c] = comments[com][:-1]
                        else:
                            msgdic[msg]["comments"][c] = comments[com]
                        c += 1
                    Done = True
                except:
                    pass
            if Done == False:
                system("rosmsg info "+msg+" > temptext.txt")
                file = open("temptext.txt")
                msginfo = file.readlines()
                file.close()
                for line in range(len(msginfo)-1):
                    if(msginfo[line][0] != " " and msginfo[line] != "\n"):
                        sp = msginfo[line].find(" ")
                        msgdic[msg]["fields"][msginfo[line][sp+1:-1]] = msginfo[line][:sp]
                        if ((msginfo[line][:sp] not in primitives) and (msginfo[line][:sp] not in edits)):
                            if(msginfo[line][:sp][-1] == "]"):
                                q = msginfo[line][:sp]
                                br = q.find("[")
                                q = q[:br]
                                if (q not in messages) and (q not in primitives):
                                    edits.append(q)
                            else:
                                edits.append(msginfo[line][:sp])
                bs = msg.find("/")
                try:
                    file = open("/opt/ros/"+distro+"/share/"+msg[:bs]+"/msg/"+msg[bs+1:]+".msg")
                    msgdic[msg]["distribution"] = "ROS/" + distro
                except:
                    file = open("/opt/rtk/"+distro+"/share/"+msg[:bs]+"/msg/"+msg[bs+1:]+".msg")
                    msgdic[msg]["distribution"] = "RTK/" + distro
                    
                comments = file.readlines()
                file.close()
                c = 1
                for com in comments:
                    while com[0] == " ":
                        com = com[1:]
                    if(com[-1] == "\n"):
                        msgdic[msg]["comments"][c] = com[:-1]
                    else:
                        msgdic[msg]["comments"][c] = com
                    c += 1
            print("Message "+ str(p) +" of "+ str(len(edits)) +" completed")

            tempdic["msgdic"] = msgdic
            tempdic["edits"] = edits
            file = open("tempMessages.json","w")
            file.write(json.dumps(tempdic))
            file.close()

        p += 1

##    filename =  inputName + "_msgs_" + date.today().strftime("%m_%d_%Y") + ".txt"
##    filename.replace("/","_")
##    msgs = open(filename,"w")
##    msgs.write("            Message Types:\n")
##    for msg in msgdic:
##        msgs.write("                  Message Type: "+msg+"\n")
##        msgs.write("                        Fields:\n")
##        for field in msgdic[msg]["fields"]:
##            msgs.write("                              "+field+" : "+msgdic[msg]["fields"][field]+"\n")
##        msgs.write("                        Comments:\n")
##        for com in msgdic[msg]["comments"]:
##            msgs.write("                              "+msgdic[msg]["comments"][com]+"\n")
##    msgs.close()

    msgitems = msgdic.items()
    msgdic = sorted(msgitems)

    filename =  inputName + "_msgs_" + date.today().strftime("%m_%d_%Y") + ".json"
    filename.replace("/","_")
    msgs = open(filename,"w")
    msgs.write(json.dumps(msgdic, indent=8))
    msgs.close() 
    remove("tempMessages.json")
    return
