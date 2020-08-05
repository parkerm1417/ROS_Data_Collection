import json
import subprocess as sp

me = sp.getoutput("whoami")
file = open("/home/" + me + "/Desktop/CompletePackageDictionary.json")
complete = file.read()
file.close()

bigdict = json.loads(complete)

file = open("/home/" + me + "/Desktop/MessagesDictionary.json")
msgs = file.read()
file.close()

messages = json.loads(msgs)

file = open("/home/" + me + "/Desktop/TopicsDictionary.json")
top = file.read()
file.close()

topics = json.loads(top)


for pack in bigdict:
    print(pack)
    for node in bigdict[pack]["nodes"]:
        full = []
        used = []
        print("      Node: " + node)
        print("            Publications:")
        for pub in bigdict[pack]["nodes"][node]["publications"]:
            print("                  Topic: " + pub)
            print("                        Message Type: " + bigdict[pack]["nodes"][node]["publications"][pub]["type"])
            full.append(bigdict[pack]["nodes"][node]["publications"][pub]["type"])
        print("            Subscriptions:")
        for sub in bigdict[pack]["nodes"][node]["subscriptions"]:
            print("                  Topic: " + sub)
            print("                        Message Type: " + bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
            full.append(bigdict[pack]["nodes"][node]["subscriptions"][sub]["type"])
        print("            Services Provided:")
        for serv in bigdict[pack]["nodes"][node]["services provided"]:
                print("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"])
                print("                        Message: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"] + "Request")
                print("                              Request Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Request")
            
                print("                  Service: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"])
                print("                        Message: " + bigdict[pack]["nodes"][node]["services provided"][serv]["name"] + "Response")
                print("                              Response Message Type: " + bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                full.append(bigdict[pack]["nodes"][node]["services provided"][serv]["type"] + "Response")
                
        print("            Message Types:")
        for msg in full:
            if msg not in used:
                print("                  Message Type: " + msg)
                print("                        Fields:")
                for field in messages[msg]["fields"]:
                    try:    
                        print("                              " + field + " : " + messages[msg]["fields"][field]["type"])
                        b = messages[msg]["fields"][field]["type"].find("[")
                        if b == -1:
                            full.append(messages[msg]["fields"][field]["type"])
                        else:
                            full.append(messages[msg]["fields"][field]["type"][:b])
                    except:
                        print("                              " + field + " : " + messages[msg]["fields"][field]["storageType"])
                print("                        Comments:")
                for com in messages[msg]["comments"]:
                    print("                              " + messages[msg]["comments"][com])
                used.append(msg)
       
 