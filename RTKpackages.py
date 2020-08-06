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

Complete["Distribution"] = distro

Topics["Distribution"] = distro
today = date.today()
Complete["Date"] = today.strftime("%x")

Topics["Date"] = today.strftime("%x")

SavedRun["date"] = today.strftime("%x")

for pack in range(len(packages)):

    subprocess.Popen("roscore")
    time.sleep(2.5)
    
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
                        topicname = ss[1:ob-1]
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
                            "type": "unknown type",
                            "data": "TBD",
                            "publishers": {node:{
                                "elementType": "node",
                                "name": node,
                                "package": pack}},
                            "subscribers": {}
                            }
                        if(datatype != "unknown type" and Topics[topicname]["type"] == "unknown type"):     
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
                            "type" : ""
                            }
                        ob = ss.find("[")      ##for formatting purposes, extraneous symbols are removed
                        bs = ss.find("/", 1, ob-1)
                        topicname = ss[1:ob-1]
                        try:        ##checks to see if the topic has already been filled with its information, and if so, only adds on the publisher/subscriber info
                            Topics[topicname]["subscribers"][node] = {
                                "elementType": "node",
                                "name": node,
                                "package": packages[pack]
                                }
                        except:     ##adds a dictionary to each topic and fills it with information, each publisher and subscriber is also assigned an empty dictionary
                            Topics[topicname] = {
                            "elementType": "topic",
                            "name": topicname,
                            "type": "unknown type",
                            "data": "TBD",
                            "publishers": {},
                            "subscribers": {node:{
                                "elementType": "node",
                                "name": node,
                                "package": packages[pack]}},
                            }
                        if(Type != "unknown type" and Topics[topicname]["type"] == "unknown type"):     
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
                    "name" : node + "/" + title,
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

                if pack != "Distribution" and pack != "Date":
                    try:
                        Complete[packages[pack]]["nodes"][node]["services provided"]["get_loggers"]["type"] = "roscpp/GetLoggers"
                        Complete[packages[pack]]["nodes"][node]["services provided"]["get_loggers"]["args"] = ""
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_logger_level"]["type"] = "roscpp/SetLoggerLevel"
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_logger_level"]["args"] = "logger level"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_exposure"]["type"] = "marti_sensor_msgs/SetExposure"
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_exposure"]["args"] = "auto_exposure time"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_parameters"]["type"] = "dynamic_reconfigure/Reconfigure"
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_parameters"]["args"] = "config"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_camera_info"]["type"] = "sensor_msgs/SetCameraInfo"
                        Complete[packages[pack]]["nodes"][node]["services provided"]["set_camera_info"]["args"] = "camera_info"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["local_xy_origin"]["type"] = "gps_common/GPSFix"
                        Topics["local_xy_origin"]["type"] = "gps_common/GPSFix"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_name"]["type"] = "std_msgs/String"
                        Topics["vehicle_name"]["type"] = "std_msgs/String"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["world_model/segmentation_data"]["type"] = "sumet_perception_msgs/GroundSegmentationData"
                        Topics["world_model/segmentation_data"]["type"] = "sumet_perception_msgs/GroundSegmentationData"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["lidar/vh_twm_costmap"]["type"] = "sumet_nav_msgs/Costmap"
                        Topics["lidar/vh_twm_costmap"]["type"] = "sumet_nav_msgs/Costmap"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["lidar/vs_costmap_surf"]["type"] = "sumet_nav_msgs/Costmap"
                        Topics["lidar/vs_costmap_surf"]["type"] = "sumet_nav_msgs/Costmap"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["lidar/vl_raw"]["type"] = "velodyne_ll/Raw"
                        Topics["lidar/vl_raw"]["type"] = "velodyne_ll/Raw"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/yaw_rate"]["type"] = "marti_sensor_msgs/Gyro"
                        Topics["localization/yaw_rate"]["type"] = "marti_sensor_msgs/Gyro"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/path_following_debug_info"]["type"] = "path_following_controller/PathFollowingDebugInfo"
                        Topics["navigation/path_following_debug_info"]["type"] = "path_following_controller/PathFollowingDebugInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/path_following_plot_data"]["type"] = "path_following_controller/PathFollowingPlotData"
                        Topics["navigation/path_following_plot_data"]["type"] = "path_following_controller/PathFollowingPlotData"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/planned_path"]["type"] = "swri_nav_msgs/PathStamped"
                        Topics["navigation/planned_path"]["type"] = "swri_nav_msgs/PathStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/planned_stop"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["navigation/planned_stop"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/predicted_path_footprint"]["type"] = "visualization_msgs/MarkerArray"
                        Topics["navigation/predicted_path_footprint"]["type"] = "visualization_msgs/MarkerArray"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/predicted_path"]["type"] = "swri_nav_msgs/PathStamped"
                        Topics["navigation/predicted_path"]["type"] = "swri_nav_msgs/PathStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/predicted_path_footprint_margin"]["type"] = "visualization_msgs/MarkerArray"
                        Topics["navigation/predicted_path_footprint_margin"]["type"] = "visualization_msgs/MarkerArray"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/pursuit_anchor_target"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                        Topics["navigation/pursuit_anchor_target"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/pursuit_arc"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                        Topics["navigation/pursuit_arc"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/classified_image"]["type"] = "sumet_perception_msgs/ClassifiedImage"
                        Topics["vision/front/classified_image"]["type"] = "sumet_perception_msgs/ClassifiedImage"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/disparity"]["type"] = "stereo_msgs/DisparityImage"
                        Topics["vision/front/disparity"]["type"] = "stereo_msgs/DisparityImage"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/imperx_stereo_pipeline/camera_/binned/image_rect_color"]["type"] = "sensor_msgs/Image"
                        Topics["vision/front/imperx_stereo_pipeline/camera_/binned/image_rect_color"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/imperx_stereo_pipeline/camera_/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["vision/front/imperx_stereo_pipeline/camera_/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/steering_target_path"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                        Topics["navigation/steering_target_path"]["type"] = "swri_nav_msgs/PathSegmentStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/stopped_for_obstacle"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["navigation/stopped_for_obstacle"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/vs_costmap_surf"]["type"] = "sumet_nav_msgs/Costmap"
                        Topics["navigation/vs_costmap_surf"]["type"] = "sumet_nav_msgs/Costmap"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/waypoint_following_parameters"]["type"] = "sumet_nav_msgs/WaypointFollowingParameters"
                        Topics["navigation/waypoint_following_parameters"]["type"] = "sumet_nav_msgs/WaypointFollowingParameters"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/auto_gear_in_reverse"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["vehicle_interface/auto_gear_in_reverse"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["world_model/heartbeat/front_stereo"]["type"] = "sumet_common_msgs/Heartbeat"
                        Topics["world_model/heartbeat/front_stereo"]["type"] = "sumet_common_msgs/Heartbeat"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["world_model/heartbeat/rear_stereo"]["type"] = "sumet_common_msgs/Heartbeat"
                        Topics["world_model/heartbeat/rear_stereo"]["type"] = "sumet_common_msgs/Heartbeat"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/brake_input"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/brake_input"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/brake_sense"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/brake_sense"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/curvature_input"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/curvature_input"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/curvature_sense"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/curvature_sense"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/curvature_setpoint"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/curvature_setpoint"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/drive_by_wire_state"]["type"] = "sumet_nav_msgs/DriveByWireState"
                        Topics["vehicle_interface/drive_by_wire_state"]["type"] = "sumet_nav_msgs/DriveByWireState"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/engine_running"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["vehicle_interface/engine_running"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/ignition_on"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["vehicle_interface/ignition_on"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/robotic_mode"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["vehicle_interface/robotic_mode"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/run_engine"]["type"] = "marti_common_msgs/BoolStamped"
                        Topics["vehicle_interface/run_engine"]["type"] = "marti_common_msgs/BoolStamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/speed_input"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/speed_input"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/speed_setpoint"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics[""]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/imu/raw"]["type"] = "sensor_msgs/Imu"
                        Topics["localization/imu/raw"]["type"] = "sensor_msgs/Imu"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/imu/is_calibrated"]["type"] = "std_msgs/Bool"
                        Topics["localization/imu/is_calibrated"]["type"] = "std_msgs/Bool"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/gps_sync"]["type"] = "std_msgs/Time"
                        Topics["localization/gps_sync"]["type"] = "std_msgs/Time"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vehicle_interface/steering_input"]["type"] = "marti_common_msgs/Float32Stamped"
                        Topics["vehicle_interface/steering_input"]["type"] = "marti_common_msgs/Float32Stamped"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/rr_nav_data"]["type"] = "rr_nav_msgs/NavData"
                        Topics["localization/rr_nav_data"]["type"] = "rr_nav_msgs/NavData"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/active_segment"]["type"] = "sumet_nav_msgs/MissionRoute"
                        Topics["navigation/active_segment"]["type"] = "sumet_nav_msgs/MissionRoute"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["front/multisense/left/image_rect_color"]["type"] = "sensor_msgs/Image"
                        Topics["front/multisense/left/image_rect_color"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["front/multisense/left/image_rect_color/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["front/multisense/left/image_rect_color/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["front/multisense/right/image_rect"]["type"] = "sensor_msgs/Image"
                        Topics["front/multisense/right/image_rect"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["navigation/behavior_debug"]["type"] = "sumet_nav_msgs/BehaviorDebugInfo"
                        Topics["navigation/behavior_debug"]["type"] = "sumet_nav_msgs/BehaviorDebugInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["front/multisense/right/image_rect/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["front/multisense/right/image_rect/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/left/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                        Topics["vision/front/left/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/left/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["vision/front/left/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/left/image_raw"]["type"] = "sensor_msgs/Image"
                        Topics["vision/front/left/image_raw"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/right/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                        Topics["vision/front/right/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/right/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["vision/front/right/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/front/right/image_raw"]["type"] = "sensor_msgs/Image"
                        Topics["vision/front/right/image_raw"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/left/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                        Topics["vision/rear/left/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/left/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["vision/rear/left/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/left/image_raw"]["type"] = "sensor_msgs/Image"
                        Topics["vision/rear/left/image_raw"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/right/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                        Topics["vision/rear/right/exposure"]["type"] = "marti_sensor_msgs/Exposure"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/right/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                        Topics["vision/rear/right/camera_info"]["type"] = "sensor_msgs/CameraInfo"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["vision/rear/right/image_raw"]["type"] = "sensor_msgs/Image"
                        Topics["vision/rear/right/image_raw"]["type"] = "sensor_msgs/Image"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["local_path"]["type"] = "sumet_nav_msgs/LocalPath"
                        Topics["local_path"]["type"] = "sumet_nav_msgs/LocalPath"
                    except:
                        pass

                    try:
                        Complete[packages[pack]]["nodes"][node]["subscriptions"]["localization/encoder_frequency"]["type"] = "marti_sensor_msgs/WheelEncoderSet"
                        Topics["localization/encoder_frequency"]["type"] = "marti_sensor_msgs/WheelEncoderSet"
                    except:
                        pass

        SavedRun["Complete"] = Complete
        SavedRun["Topics"] = Topics
        file = open("PreviousRun.json","w")
        file.write(json.dumps(SavedRun))
        file.close()

        print("Package "+ str(pack+1) +" of "+ str(len(packages)) + " complete")
        system("rosnode kill -a")
        system("killall -9 rosmaster")
        
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

for pack in Complete:
    if pack != "Distribution" and pack != "Date":
        for node in Complete[pack]["nodes"]:
                for sub in Complete[pack]["nodes"][node]["subscriptions"]:
                    if Topics[sub]["type"] == "":
                        Complete[pack]["nodes"][node]["subscriptions"][sub]["type"] = "unknown type"
                    else:
                        Complete[pack]["nodes"][node]["subscriptions"][sub]["type"] = Topics[sub]["type"]
                        
print("")

if not messagescheck:
    messageFunc(packages,distro,inputName,Complete)
    SavedRun["messagescheck"] = True
    file = open("PreviousRun.json","w")
    file.write(json.dumps(SavedRun))
    file.close()
    print("")
if not servicescheck:
    serviceFunc(packages,distro,inputName,Complete)
    SavedRun["servicescheck"] = True
    file = open("PreviousRun.json","w")
    file.write(json.dumps(SavedRun))
    file.close()
    print("")

top = open(inputName + "_TopicsDictionary_" + date.today().strftime("%m_%d_%Y") + ".json", "w")
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
