from os import listdir,system,remove
import subprocess
import time
import json
from datetime import date

####################################################################################################################
##This funtion gets all the messages from the Complete dictionary and finds all messsages related to those messages
##to produce a complete dictionary for every message utilized by a package. Messages are normal messages but also
##service messages. For each message, information about the fields of the message and any comments in the .msg file
##are gathered and outputted into a .json file for easy parsing in other programs.
####################################################################################################################
def messageFunc(packages,distro,inputName,Complete):
    primitives = ["unknown type","char","byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]"]
    edits = []
    
    ##  Fills edits with all messages from the Complete dictrionary created in packages.py      
    for pack in Complete:
        if pack != "Distribution" and pack != "Date":
            for node in Complete[pack]["nodes"]:
                for pub in Complete[pack]["nodes"][node]["publications"]:
                    if Complete[pack]["nodes"][node]["publications"][pub]["type"] not in edits:
                        edits.append(Complete[pack]["nodes"][node]["publications"][pub]["type"])
                for sub in Complete[pack]["nodes"][node]["subscriptions"]:
                    if Complete[pack]["nodes"][node]["subscriptions"][sub]["type"] not in edits:
                        edits.append(Complete[pack]["nodes"][node]["subscriptions"][sub]["type"])
                for serv in Complete[pack]["nodes"][node]["services provided"]:
                    if Complete[pack]["nodes"][node]["services provided"][serv]["type"]+"Request" not in edits:
                        edits.append(Complete[pack]["nodes"][node]["services provided"][serv]["type"]+"Request")
                        edits.append(Complete[pack]["nodes"][node]["services provided"][serv]["type"]+"Response")

                                 
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

    ##Loops through all messages in edits and compiles information about them into file
    for msg in edits:
        if (msg not in msgdic) and (msg != "unknown type") and (msg[:7] != "Unknown") and (msg[:8] != " Unknown"):
            Done = False
            bs = msg.find("/")
            msgdic[msg] = {
                "package" : msg[:bs],
                "distribution" : "",
                "fields": {},
                "comments": {}
                }
            ##Determines if message is a service request message
            if(msg[-7:] == "Request"):
                try:
                    system("rossrv info "+msg[:-7]+" > temptext.txt")
                    file = open("temptext.txt")
                    msginfo = file.readlines()
                    file.close()
                    ##Finds the line taht divides the request and response information
                    try:
                        split = msginfo.index("---\n")
                        
                    except:
                        split = msginfo.index("---")

                    ##Goes through each line in the request section
                    for line in range(0,split):
                        if(msginfo[line][0] != " " and msginfo[line] != "\n"):
                            sp = msginfo[line].find(" ")
                            msgdic[msg]["fields"][msginfo[line][sp+1:-1]] = msginfo[line][:sp]
                            if ((msginfo[line][:sp] not in primitives) and (msginfo[line][:sp] not in edits)):
                                if(msginfo[line][:sp][-1] == "]"):
                                    q = msginfo[line][:sp]
                                    br = q.find("[")
                                    q = q[:br]

                                    ##If a field utilized by this message is another message, the program checks to
                                    ##see if that message is in the list of messages already. If not it is added for
                                    ##later data acquisition.
                                    if (q not in edits) and (q not in primitives):
                                        edits.append(q)
                                else:
                                    edits.append(msginfo[line][:sp])
                    bs = msg.find("/")

                    ##Opens the .srv file to get the comment information
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

            ##Determines if message is service response message. For more detailed information see section above    
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
                                    if (q not in edits) and (q not in primitives):
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
            ##If message is not a service message than it is a normal message and gets processed below.
            ##This section works very similar to the other sections, except there is no request and response split
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
                                if (q not in edits) and (q not in primitives):
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

            ##Prints out a message to let user know how the program is progressing
            print("Message "+ str(p) +" of "+ str(len(edits)) +" completed")

            ##Dumps temporary dictionary to file for later use if the program is stopped and the resumed.
            tempdic["msgdic"] = msgdic
            tempdic["edits"] = edits
            file = open("tempMessages.json","w")
            file.write(json.dumps(tempdic))
            file.close()

        p += 1
        
    ##Creates file and then dumps all of the message information into the file. Then deletes the temporary save file
    filename =  inputName + "_msgs_" + date.today().strftime("%m_%d_%Y") + ".json"
    filename.replace("/","_")
    msgs = open(filename,"w")
    msgs.write(json.dumps(msgdic, indent=8))
    msgs.close() 
    remove("tempMessages.json")
    return
