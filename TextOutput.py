import json
import subprocess as sp
from os import system

me = sp.getoutput("whoami")
print("The file names you are about to enter should\nall come from the same run of RTKpackages.py")
packagedict = input("Enter the exact file path of the package dictionary .json\nfile you wish to get output from.\nExample: /home/mie/Desktop/packages.json\n")
print()
file = open(packagedict)
complete = file.read()
file.close()

bigdict = json.loads(complete)

messagedict = input("Enter the exact file path of the messages dictionary .json\nfile you wish to get output from.\nExample: /home/mie/Desktop/messages.json\n")
print()
file = open(messagedict)
msgs = file.read()
file.close()

messages = json.loads(msgs)

topicdict = input("Enter the exact file path of the topics dictionary .json\nfile you wish to get output from.\nExample: /home/mie/Desktop/topics.json\n")
print()
file = open(topicdict)
top = file.read()
file.close()

topics = json.loads(top)

system("mkdir /home/" + me + "/Desktop/Architecture_Documents")
system("mkdir /home/" + me + "/Desktop/Architecture_Documents/ROS")
system("mkdir /home/" + me + "/Desktop/Architecture_Documents/RTK")
c = 0
for pack in bigdict:
    if pack == "Distribution" or pack == "Date":
        print("skipped")
        continue
    if (bigdict[pack]["distribution"][:3] == "ROS"):
        system("mkdir /home/" + me + "/Desktop/Architecture_Documents/ROS/" + pack)
        for node in bigdict[pack]["nodes"]:
            try:
                file = open("/home/" + me + "/Desktop/Architecture_Documents/ROS/" + pack + "/" + node + ".txt", "x")
            except:
                continue
            file.write("Package: " + pack)
            full = []
            used = []
            file.write("      Node: " + node)
            file.write("            Publications:")
            for pub in bigdict[pack]["nodes"][node]["publications"]:
                file.write("                  Topic: " + pub)
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["publications"][pub]["type"])
                full.append(bigdict[pack]["nodes"][node]["publications"][pub]["type"])
            file.write("            Subscriptions:")
            for sub in bigdict[pack]["nodes"][node]["subscriptions"]:
                file.write("                  Topic: " + sub)
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
                full.append(bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
            file.write("            Services Provided:")
            for serv in bigdict[pack]["nodes"][node]["services provided"]:
                file.write("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"])
                file.write("                        Service Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"])
                file.write("                              Request Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")
                file.write("                              Response Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")

                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")   
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                    
            file.write("            Message Types:")
            for msg in full:
                if msg not in used:
                    file.write("                  Message Type: " + msg)
                    file.write("                        Fields:")
                    for field in messages[msg]["fields"]:
                        try:    
                            file.write("                              " + field + " : " + messages[msg]["fields"][field]["type"])
                            b = messages[msg]["fields"][field]["type"].find("[")
                            if b == -1:
                                full.append(messages[msg]["fields"][field]["type"])
                            else:
                                full.append(messages[msg]["fields"][field]["type"][:b])
                        except:
                            file.write("                              " + field + " : " + messages[msg]["fields"][field]["storageType"])
                    file.write("                        Comments:")
                    for com in messages[msg]["comments"]:
                        file.write("                              " + messages[msg]["comments"][com])
                    used.append(msg)

    elif (bigdict[pack]["distribution"][:3] == "RTK"):
        system("mkdir /home/" + me + "/Desktop/Architecture_Documents/RTK/" + pack)
        for node in bigdict[pack]["nodes"]:
            try:
                file = open("/home/" + me + "/Desktop/Architecture_Documents/RTK/" + pack + "/" + node + ".txt", "x")
            except:
                continue
            file.write("Package: " + pack)
            full = []
            used = []
            file.write("      Node: " + node)
            file.write("            Publications:")
            for pub in bigdict[pack]["nodes"][node]["publications"]:
                file.write("                  Topic: " + pub)
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["publications"][pub]["type"])
                full.append(bigdict[pack]["nodes"][node]["publications"][pub]["type"])
            file.write("            Subscriptions:")
            for sub in bigdict[pack]["nodes"][node]["subscriptions"]:
                file.write("                  Topic: " + sub)
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
                full.append(bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
            file.write("            Services Provided:")
            for serv in bigdict[pack]["nodes"][node]["services provided"]:
                file.write("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"])
                file.write("                        Service Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"])
                file.write("                              Request Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")
                file.write("                              Response Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")

                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")   
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                    
            file.write("            Message Types:")
            for msg in full:
                if msg not in used:
                    file.write("                  Message Type: " + msg)
                    file.write("                        Fields:")
                    for field in messages[msg]["fields"]:
                        try:    
                            file.write("                              " + field + " : " + messages[msg]["fields"][field]["type"])
                            b = messages[msg]["fields"][field]["type"].find("[")
                            if b == -1:
                                full.append(messages[msg]["fields"][field]["type"])
                            else:
                                full.append(messages[msg]["fields"][field]["type"][:b])
                        except:
                            file.write("                              " + field + " : " + messages[msg]["fields"][field]["storageType"])
                    file.write("                        Comments:")
                    for com in messages[msg]["comments"]:
                        file.write("                              " + messages[msg]["comments"][com])
                    used.append(msg)
    c + 1
    print("Package " + str(c) + " of " + str(len(bigdict)-2) + " completed")
print("Program complete. See Desktop for Architecture_Documents folder.")
