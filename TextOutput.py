import json
import subprocess as sp
from os import system

primitives = ["byte","bool","int8","uint8","int16","uint16","int32","uint32","int64","uint64","float32","float64","string","time","duration","bool[]","int8[]","uint8[]","int16[]","uint16[]","int32[]","uint32[]","int64[]","uint64[]","float32[]","float64[]","string[]","time[]","duration[]", "float64[4]", "float64[9]", "float64[12]","float64[36]","unknown type","char"]

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
            file.write("Package: " + pack + "\n")
            full = []
            used = []
            file.write("      Node: " + node + "\n")
            file.write("            Publications:\n")
            for pub in bigdict[pack]["nodes"][node]["publications"]:
                file.write("                  Topic: " + pub + "\n")
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["publications"][pub]["type"] + "\n")
                if bigdict[pack]["nodes"][node]["publications"][pub]["type"] not in primitives:
                    full.append(bigdict[pack]["nodes"][node]["publications"][pub]["type"])
            file.write("            Subscriptions:\n")
            for sub in bigdict[pack]["nodes"][node]["subscriptions"]:
                file.write("                  Topic: " + sub  + "\n")
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"] + "\n")
                if bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"] not in primitives:
                    full.append(bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
            file.write("            Services Provided:\n")
            for serv in bigdict[pack]["nodes"][node]["services provided"]:
                file.write("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"] + "\n")
                file.write("                        Service Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "\n")
                file.write("                              Request Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request\n")
                file.write("                              Response Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response\n")

                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")   
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                    
            file.write("            Message Types:\n")
            for msg in full:
                if msg not in used:
                    file.write("                  Message Type: " + msg + "\n")
                    file.write("                        Fields:\n")
                    for field in messages[msg]["fields"]:    
                        file.write("                              " + field + " : " + messages[msg]["fields"][field] + "\n")
                        b = messages[msg]["fields"][field].find("[")
                        if b == -1:
                            if messages[msg]["fields"][field] not in primitives:
                                full.append(messages[msg]["fields"][field])
                        else:
                            if messages[msg]["fields"][field][:b] not in primitives:
                                full.append(messages[msg]["fields"][field][:b])
                    file.write("                        Comments:\n")
                    for com in messages[msg]["comments"]:
                        file.write("                              " + messages[msg]["comments"][com] + "\n")
                    used.append(msg)

    elif (bigdict[pack]["distribution"][:3] == "RTK"):
        system("mkdir /home/" + me + "/Desktop/Architecture_Documents/RTK/" + pack)
        for node in bigdict[pack]["nodes"]:
            try:
                file = open("/home/" + me + "/Desktop/Architecture_Documents/RTK/" + pack + "/" + node + ".txt", "x")
            except:
                continue
            file.write("Package: " + pack + "\n")
            full = []
            used = []
            file.write("      Node: " + node + "\n")
            file.write("            Publications:\n")
            for pub in bigdict[pack]["nodes"][node]["publications"]:
                file.write("                  Topic: " + pub + "\n")
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["publications"][pub]["type"] + "\n")
                if bigdict[pack]["nodes"][node]["publications"][pub]["type"] not in primitives:
                    full.append(bigdict[pack]["nodes"][node]["publications"][pub]["type"])
            file.write("            Subscriptions:\n")
            for sub in bigdict[pack]["nodes"][node]["subscriptions"]:
                file.write("                  Topic: " + sub  + "\n")
                file.write("                        Message Type: " + bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"] + "\n")
                if bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"] not in primitives:
                    full.append(bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
            file.write("            Services Provided:\n")
            for serv in bigdict[pack]["nodes"][node]["services provided"]:
                file.write("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"] + "\n")
                file.write("                        Service Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "\n")
                file.write("                              Request Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request\n")
                file.write("                              Response Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response\n")

                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")   
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                    
            file.write("            Message Types:\n")
            for msg in full:
                if msg not in used:
                    file.write("                  Message Type: " + msg + "\n")
                    file.write("                        Fields:\n")
                    for field in messages[msg]["fields"]:    
                        file.write("                              " + field + " : " + messages[msg]["fields"][field] + "\n")
                        b = messages[msg]["fields"][field].find("[")
                        if b == -1:
                            if messages[msg]["fields"][field] not in primitives:
                                full.append(messages[msg]["fields"][field])
                        else:
                            if messages[msg]["fields"][field][:b] not in primitives:
                                full.append(messages[msg]["fields"][field][:b])
                    file.write("                        Comments:\n")
                    for com in messages[msg]["comments"]:
                        file.write("                              " + messages[msg]["comments"][com] + "\n")
                    used.append(msg)

    file.close()
    c += 1
    print("Package " + str(c) + " of " + str(len(bigdict)-2) + " completed")
print("Program complete. See Desktop for Architecture_Documents folder.")
