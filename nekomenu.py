#!/usr/bin/env python

#Dynamic menu for the Neko project.
#Usable with any openbox desktop.

import os, hashlib

MENUFOLDER = os.path.expanduser("~/.config/nekomenu/")
APPSDIR = "/usr/share/applications"

#Functions
def updateMenuFiles():
    import xml.etree.ElementTree as ET    
    APPCATEGORIES = ["Audio", "Video", "Development", "Education", "Game", "Graphics", "Network", "Office", "Science", "Settings", "System", "Utility", "Other"]    
    menuRoot = ET.Element("openbox_pipe_menu")
    
    for category in APPCATEGORIES:
        elem = ET.Element("menu", {"id" : "neko_" + category, "label" : category})
        menuRoot.append(elem)
    
    APPS = []
    appList = os.listdir(APPSDIR)
    appHash = hashlib.sha1()
    
    for app in appList:
        appHash.update(app)
        if not ".desktop" in app:
            continue
        appFile = open(os.path.join(APPSDIR, app), "rb")
        appInfo = appFile.read(os.stat(os.path.join(APPSDIR, app)).st_size)
        appFile.close()
        if appInfo.find("Categories=") == -1:
            continue
        #Name
        appName = appInfo[appInfo.find("Name=")+5:appInfo.find("\n", appInfo.find("Name=")+5)]
        
        #Command
        appCommand = appInfo[appInfo.find("Exec=")+5:appInfo.find("\n", appInfo.find("Exec=")+5)]
        if "%" in appCommand:
            appCommand = appCommand[0:appCommand.find("%")-1]
        checkTerminal = appInfo[appInfo.find("Terminal=")+9:appInfo.find("\n", appInfo.find("Terminal=")+9)]
        if checkTerminal in ("True", "TRUE", "true"):
            appCommand = "x-terminal-emulator -e " + appCommand
        
        #Categories
        appCats = appInfo[appInfo.find("Categories=")+11:appInfo.find("\n", appInfo.find("Categories=")+11)].split(";")
        if "" in appCats:
            appCats.remove("")
        appCategory = "Other"
        for cat in appCats:
            if cat in APPCATEGORIES:
                appCategory = cat
        
        #Summarize information and put in XML format. This is ugly, but blame it on openbox's pipe menu API.
        firstLevel = ET.Element("item", {"label": appName})
        secondLevel = ET.Element("action", {"name": "Execute"})
        thirdLevel = ET.Element("execute")
        thirdLevel.text = appCommand
        
        firstLevel.text = "\n"
        firstLevel.tail = "\n"
        secondLevel.text = "\n\t"
        secondLevel.tail = "\n"
        thirdLevel.tail = "\n"
        
        secondLevel.append(thirdLevel)
        firstLevel.append(secondLevel)
        
        if menuRoot.find("./menu/[@label='" + appCategory + "']") != None:
            menuRoot.find("./menu/[@label='" + appCategory + "']").append(firstLevel)
        else:
            menuRoot.find("./menu/[@label='Other']").append(firstLevel)
    
    hashFile = open(os.path.join(MENUFOLDER, "apphash"), "wb")
    hashFile.write(appHash.hexdigest())
    hashFile.close()
    
    emptyElements = []
    for element in menuRoot:
        if len(element) == 0:
            emptyElements.append(element)
    for element in emptyElements:
        menuRoot.remove(element)
            
    nekoMenu = ET.ElementTree(menuRoot)
    nekoMenu.write(os.path.join(MENUFOLDER, "nekomenu.xml"))

#Displays the menu in ~/.config/nekomenu/nekomenu.xml
def displayMenu():
    menuFile = open(os.path.join(MENUFOLDER, "nekomenu.xml"), "rb")
    menuOutput = menuFile.read(os.stat(os.path.join(MENUFOLDER, "nekomenu.xml")).st_size)
    menuFile.close()
    print menuOutput

#Main Script

#First time only. Create necessary folders and files.
if not os.path.isdir(MENUFOLDER):
    os.makedirs(MENUFOLDER)
if not os.path.isfile(os.path.join(MENUFOLDER, "apphash")):
    hashFile = open(os.path.join(MENUFOLDER, "apphash"), "wb")
    hashFile.close()
    updateMenuFiles()

#Gets the data from ~/.config/nekomenu/apphash and compares it to the current state of /usr/share/applications
#If they're different, update the menu then display. Otherwise, just display.
hashFile = os.open(os.path.join(MENUFOLDER, "apphash"), os.O_RDONLY)
currentAppHash = os.read(hashFile, 64)
os.close(hashFile)

appList = os.listdir(APPSDIR)
appHash = hashlib.sha1()
for item in appList:
    appHash.update(item)
    
if appHash.hexdigest() == currentAppHash:
    displayMenu()
else:
    updateMenuFiles()
    displayMenu()
