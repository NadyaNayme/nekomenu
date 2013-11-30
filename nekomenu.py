#!/usr/bin/env python

#Dynamic menu for the Neko project.
#Usable with any openbox desktop.

import os, hashlib

MENUFOLDER = os.path.expanduser("~/.config/nekomenu/")
APPSDIR = "/usr/share/applications"

#Functions
def updateMenuFiles():
    #A list of the main application categories defined by freedesktop.org
    APPCATEGORIES = ["Accessories", "Audio", "Video", "Development", "Education", "Game", "Graphics", "Network", "Office", "Science", "Settings", "System", "Utilities"]
    #Empty list to be populated by all applications
    APPS = []
    appList = os.listdir(APPSDIR)
    appHash = hashlib.sha1()
    for app in appList:
        #If it isn't a .desktop file, ignore it
        if not ".desktop" in app:
            continue
        #Puts the whole .desktop file in a string
        appFile = open(os.path.join(APPSDIR, app), "rb")
        appInfo = appFile.read(os.stat(os.path.join(APPSDIR, app)).st_size)
        appFile.close()
        #If it doesn't have a "Categories" entry, ignore it
        if appInfo.find("Categories=") == -1:
            continue
        #Find the application name
        appName = appInfo[appInfo.find("Name=")+5:appInfo.find("\n", appInfo.find("Name=")+5)]
        #Find the application command and remove the %f/%u part
        appCommand = appInfo[appInfo.find("Exec=")+5:appInfo.find("\n", appInfo.find("Exec=")+5)]
        if "%" in appCommand:
            appCommand = appCommand[0:appCommand.find("%")-1]
        #Check if application is supposed to be executed in a Terminal
        TRUESTRINGS = ("True", "TRUE", "true")
        FALSESTRINGS = ("False", "FALSE", "false")
        checkTerminal = appInfo[appInfo.find("Terminal=")+9:appInfo.find("\n", appInfo.find("Terminal=")+9)]
        if checkTerminal in TRUESTRINGS:
            appCommand = "x-terminal-emulator -e " + appCommand
        #Find which of the main categories fits this application, if none, put it in "Accessories" 
        appCats = appInfo[appInfo.find("Categories=")+11:appInfo.find("\n", appInfo.find("Categories=")+11)].split(";")
        if "" in appCats:
            appCats.remove("")
        appCategory = "Accessories"
        for cat in appCats:
            if cat in APPCATEGORIES:
                appCategory = cat   
        APPS.append({"name":appName, "category":appCategory, "command":appCommand})
        #Add this application to the main hash
        appHash.update(app)
    #Start writing the menu to ~/.config/nekomenu/nekomenu.xml
    menuFile = open(os.path.join(MENUFOLDER, "nekomenu.xml"), "wb")
    menuFile.write("<openbox_pipe_menu>")
    for category in APPCATEGORIES:
        menuString = ""
        for app in APPS:
            if app["category"] == category:
                menuString += "\n\t\t<item label=\"" + app["name"] + "\">\n\t\t\t<action name=\"Execute\">\n\t\t\t\t<execute>" + app["command"] + "</execute>\n\t\t\t</action>\n\t\t</item>"
        #If the whole category is empty, do not put an entry for it (to avoid empty menus)
        if menuString != "":
            menuFile.write("\n\t<menu id=\"neko_" + category + "\" label=\"" + category + "\">")
            menuFile.write(menuString)
            menuFile.write("\n\t</menu>")
        
    menuFile.write("\n</openbox_pipe_menu>")
    menuFile.close()
    #Write the hash to ~/.config/nekomenu/apphash
    hashFile = open(os.path.join(MENUFOLDER, "apphash"), "wb")
    hashFile.write(appHash.hexdigest())
    hashFile.close()

#Displays the menu in ~/.config/nekomenu/nekomenu.xml
def displayMenu():
    menuFile = open(os.path.join(MENUFOLDER, "nekomenu.xml"), "rb")
    menuOutput = menuFile.read(os.stat(os.path.join(MENUFOLDER, "nekomenu.xml")).st_size)
    print menuOutput
    menuFile.close()

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
currentAppHash = os.read(hashFile, 40)
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
