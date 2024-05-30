#---------------------------
#   Import Libraries
#---------------------------
import os
import sys
import json
import codecs
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Marked Challenge"
Website = "https://alexcollini.dev"
Description = ""
Creator = "Pipodi"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

loadedData = {}

# Array with the name of the Tarkov keycards, used for input sanity check
keycards = ["black", "red", "green", "yellow", "blue", "violet"]

#---------------------------
#   Reads JSON file
#---------------------------
def readData(file_path):
    try:
        with codecs.open(file_path, encoding="utf-8-sig", mode="r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return None

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    ScriptSettings = MySettings(SettingsFile)
    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command and Parent.HasPermission(data.User,ScriptSettings.Permission,ScriptSettings.Info):

        # Reads persisted data for marked and keycards count
        loadedData = readData(os.path.join(os.path.dirname(__file__), "Settings", "data.json"))
        
        # If the message is "!marked" only, it should only sent the current situation
        if str(data.GetParamCount()) == "1":
            Parent.Log(ScriptName, "No params, send current situation")
            # Sends message to Twitch chat
            Parent.SendTwitchMessage(ScriptSettings.Response.format(loadedData["NMarked"], loadedData["NKeycard"], loadedData["NBlack"], loadedData["NRed"], loadedData["NGreen"], loadedData["NYellow"], loadedData["NBlue"], loadedData["NViolet"])) 
            return

        # Gets params from the message, should have this syntax "!marked card:value,card:value"
        payload = data.GetParam(1).lower()

        # Increases the number of the opened marked rooms, regardless of the loot
        loadedData["NMarked"] = str(int(loadedData["NMarked"]) + 1)

        # If we had no keycards, "0" should be passed as param. This if skips the update of the keycards count
        if payload == '0':
            Parent.Log(ScriptName, "Opened, but no keycard")
            dataPath = os.path.join(os.path.dirname(__file__), "Settings\data.json")
            # Updates the persisted data for another iteration
            with open(dataPath, 'w') as json_file:
                json.dump(loadedData, json_file, indent=4)
            # Sends message to Twitch chat
            Parent.SendTwitchMessage(ScriptSettings.Response.format(loadedData["NMarked"], loadedData["NKeycard"], loadedData["NBlack"], loadedData["NRed"], loadedData["NGreen"], loadedData["NYellow"], loadedData["NBlue"], loadedData["NViolet"])) 
            return   
        
        # Splits the params by comma, resulting in an array of couples "card:value"
        cardsAndValues = payload.split(",")

        # Foreach to update every keycard count
        for x in cardsAndValues:
            couple = x.split(":")
            # Input sanity checks
            if not couple[1].isdigit() or couple[0].isdigit() or not couple[0] in keycards:
                # Rollback the opened marked
                loadedData["NMarked"] = str(int(loadedData["NMarked"]) - 1)
                Parent.SendTwitchMessage("Wrong syntax, should be !marked card:value,card:value. Value must be a numeric value. Card should be the color of one of the Tarkov keycards.")
                return
            
            # Updates the cards count
            if couple[0].lower() == "black":
                loadedData["NBlack"] = str(int(loadedData["NBlack"]) + int(couple[1]))
            elif couple[0].lower() == "red":
                loadedData["NRed"] = str(int(loadedData["NRed"]) + int(couple[1]))
            elif couple[0].lower() == "green":
                loadedData["NGreen"] = str(int(loadedData["NGreen"]) + int(couple[1]))
            elif couple[0].lower() == "yellow":
                loadedData["NYellow"] = str(int(loadedData["NYellow"]) + int(couple[1]))
            elif couple[0].lower() == "blue":
                loadedData["NBlue"] = str(int(loadedData["NBlue"]) + int(couple[1]))
            elif couple[0].lower() == "violet":
                loadedData["NViolet"] = str(int(loadedData["NViolet"]) + int(couple[1]))

        # Sums all the updated keycard counts to get the total
        loadedData["NKeycard"] = str(int(loadedData["NBlack"]) + int(loadedData["NRed"]) + int(loadedData["NGreen"]) + int(loadedData["NYellow"]) + int(loadedData["NBlue"]) + int(loadedData["NViolet"]))

        dataPath = os.path.join(os.path.dirname(__file__), "Settings\data.json")

        # Updates the persisted data for another iteration
        with open(dataPath, 'w') as json_file:
            json.dump(loadedData, json_file, indent=4)
        # Sends message to Twitch chat
        Parent.SendTwitchMessage(ScriptSettings.Response.format(loadedData["NMarked"], loadedData["NKeycard"], loadedData["NBlack"], loadedData["NRed"], loadedData["NGreen"], loadedData["NYellow"], loadedData["NBlue"], loadedData["NViolet"]))    
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    
    if "$myparameter" in parseString:
        return parseString.replace("$myparameter","I am a cat!")
    
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.__dict__ = json.loads(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return
