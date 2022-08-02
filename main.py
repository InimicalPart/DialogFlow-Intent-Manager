
# ***********************************************
# *  Copyright (c) 2022 InimicalPart 
# *  All rights reserved.
# *
# *  This program is under the MIT license.
# **********************************************

from genericpath import isfile
import re
import time
import google.cloud.dialogflow_v2 as dialogflow
import os
import json
import shutil
import argparse
from colorama import Fore, Back, Style
parser = argparse.ArgumentParser(description="DialogFlow Intent Manager",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-c", "--create", action="store_true", help="delete intents")
parser.add_argument("-d", "--delete", action="store_true", help="create intents")
parser.add_argument("-l", "--list", action="store_true", help="list intents")
parser.add_argument("-o", "--only-names", action="store_true", help="only show names (list intents)")
parser.add_argument("-s", "--silent", action="store_true", help="silent mode, no output, only errors")
parser.add_argument("-n", "--no-banner", action="store_true", help="no banner")
parser.add_argument("-b", "--backup-intents", action="store_true", help="backup intents")
parser.add_argument("-k", "--create-done", action="store_true", help="create done folder")
parser.add_argument("-p", "--project-id", help="project id")
parser.add_argument("-i", "--intents-folder", help="folder where intents are kept (will create 'done' and 'bkup' (if backup is enabled) in the folder)")
parser.add_argument("-a", "--authorization-path", help="path to the authorization file")
args = parser.parse_args()
arguments = vars(args)
# print(arguments)
config = {}
try:
    config = json.load(open('config.json'))
except:
    if arguments["project_id"] is None or arguments["authorization_path"] is None:
        print('config.json not found or is invalid')
        exit()
    if (arguments["project_id"] is None and arguments["authorization_path"] is not None) or (arguments["project_id"] is not None and arguments["authorization_path"] is None):
        print('Config file does not exist, and insufficient arguments were provided, please provide both project_id and authorization_path')
        exit()
    pass

#if two of arguments["create"], arguments["delete"], arguments["list"] are True, then error
if (arguments["create"] and arguments["delete"]) or (arguments["create"] and arguments["list"]) or (arguments["delete"] and arguments["list"]):
    print('You can only choose one of the options')
    exit()
config["project_id"] = ""
config["authFile"] = ""
config["backupIntentFiles"] = False
if arguments["project_id"] is not None:
    config["project_id"] = arguments["project_id"]
if arguments["authorization_path"] is not None:
    config["authFile"] = re.sub(r"\\","/",arguments["authorization_path"])
if arguments["backup_intents"] is True:
    config["backupIntentFiles"] = True


if "createDoneFolder" not in config:
  config["createDoneFolder"] = False
mainPath=None
try:
    mainPath = re.sub("\/$","",re.sub(r"\\","/",arguments["intents_folder"]))
    if not os.path.isfile(arguments["intents_folder"]):
        mainPath = mainPath + "/"
except:
    pass
if mainPath is None:
    mainPath = "./intents/"

if config["createDoneFolder"] is True:
    os.makedirs(mainPath + 'done', exist_ok=True)
if config["backupIntentFiles"] is True:
    os.makedirs(mainPath + 'bkup', exist_ok=True)

try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['authFile']
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(config['project_id'], "created_by_inimicalpart")
except:
    print('{} not found, is invalid, or project not found on DialogFlow'.format(config['authFile']))
    exit()

def list_intents(project_id="", onlyNames = False):
    if project_id == "" and config["project_id"] is not None:
        project_id = config["project_id"]
    if project_id == "":
        print("Project ID not found")
        exit()
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent})
    if onlyNames is True:
        newIntents = []
        for intent in intents:
            newIntents.append(intent.display_name)
        return newIntents
    return intents
def get_intent(project_id, intent_name):
    all_intents = list_intents(project_id)
    for intent in all_intents.intents:
        if intent.display_name == intent_name:
            return intent
    return None
def delete_intent(project_id, intent_id):
    intents_client = dialogflow.IntentsClient()
    intent_path = intents_client.intent_path(project_id, intent_id)
    intents_client.delete_intent(request={"name": intent_path})

def get_fallback_intent(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent})
    for intent in intents:
        if intent.is_fallback is True:
            return intent
    return None



def create_intent(project_id, display_name, training_phrases_parts, message_texts, parameters=[], intentData={}):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_prt in training_phrases_parts:
        parts = []
        for training_phrases_part in training_phrases_prt:
            if isinstance(training_phrases_part, dict):
                if "alias" in training_phrases_part and "entityType" in training_phrases_part:
                    parts.append(dialogflow.types.Intent.TrainingPhrase.Part(
                        text=training_phrases_part['text'],
                        entity_type=training_phrases_part['entityType'],
                        alias=training_phrases_part['alias'],
                        user_defined=True
                    ))
                else:
                    parts.append(dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part["text"]))
            else:
                parts.append(dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part))
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=parts)
        training_phrases.append(training_phrase)
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    newParameters = []
    if len(parameters) > 0:
        print(len(parameters))
        for parameter in parameters:
            newParameters.append(dialogflow.Intent.Parameter(
                name="",
                display_name=parameter['name'],
                value=parameter['value'],
                default_value=parameter['defaultValue'],
                entity_type_display_name=parameter['dataType'],
                mandatory=parameter['required'],
                prompts=parameter['prompts'],
                is_list=parameter['isList']
            ))
    rev = intentData['auto']
    if rev is True:
        rev = False
    else:
        rev = True
    intents_client.create_intent(
        request={"parent": parent, "intent": dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
        parameters=newParameters,

        webhook_state=intentData["webhookUsed"],
        priority=intentData["priority"],
        is_fallback=intentData["fallbackIntent"],
        ml_disabled=rev,
        live_agent_handoff=intentData["liveAgentHandoff"],
        end_interaction=intentData["endInteraction"],
        events=intentData["events"],

        # All other fields may be added in the future.

    )}
    )

def create_intents():
    if arguments["silent"] is False:
        print("Checking if access to DialogFlow is granted...")
    try:
        list_intents(config['project_id'])
    except Exception as e :
        print("Access Denied, Reason: {}".format(e))
        exit()
    if arguments["silent"] is False:
        print(Fore.GREEN + "Access Granted!" + Fore.RESET)

    filenames = next(os.walk(mainPath), (None, None, []))[2]
    newfiles = []
    try:
        filenames.remove(".gitkeep")
    except:
        pass
    if len(filenames) == 0:
        print(Fore.RED + "No intents found in {}, exiting...".format(mainPath) + Fore.RESET)
        exit()
    if arguments["silent"] is False:
        print("Doing checks against the files...\n")
    for filename in filenames:
        if arguments["silent"] is False:
            print("Checking {}... ".format(filename), end="")
        if filename.endswith(".json"):
            try:
                data = json.load(open(mainPath + filename))
            except:
                print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "invalid data"))
                exit()
            if "name" not in data:
                print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "intent has no name"))
                exit()
            if "userSays" not in data:
                print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "intent has no userSys"))
                exit()
            if len(data["userSays"]) == 0:
                print(Fore.RED + "FAIL"+Fore.RESET+", Reason: {}".format( "intent has no items in userSys"))
                exit()
            if arguments["silent"] is False:
                print(Fore.GREEN+"OK"+Fore.RESET)
            newfiles.append(filename)
        else:
            print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "not .json"))
        
    for filename in newfiles:
        data = json.load(open(mainPath + filename))
        # print(data)
        if arguments["silent"] is False:
            print("Adding intent with name '{}' specified by '{}'... ".format(data["name"], filename), end="")
        trainingPhrases = []
        responses = []
        dataCopy = data.copy()
        intentName = data["name"]
        if get_intent(config['project_id'], intentName) is not None:
            if arguments["silent"] is False:
                print(Fore.LIGHTBLACK_EX+ "SKIPPED, alreadyexists" + Fore.RESET)
            continue
        for userSays in data["userSays"]:
            a = []
            if isinstance(userSays["data"], list):
                for data in userSays["data"]:
                    if "meta" in data and "alias" in data:
                        newObj = {}
                        newObj["text"] = data["text"]
                        newObj["userDefined"] = True
                        newObj["entityType"] = data["meta"]
                        newObj["alias"] = data["alias"]
                        a.append(newObj)
                    else:
                        a.append(data["text"])
            else:
                trainingPhrases.append(userSays["data"].text)
            
            trainingPhrases.append(a)
        if "responses" in dataCopy:
            for response in dataCopy["responses"]:
                if "messages" in response:
                    if len(response["messages"]) > 0:
                        if "speech" in response["messages"][0]:
                            responses = response["messages"][0]["speech"]
        

        parametersyay = []
        if "responses" in dataCopy:
            for response in dataCopy["responses"]:
                if "parameters" in response:
                    parametersyay = response["parameters"]


        try:
            create_intent(config['project_id'], intentName, trainingPhrases, responses, parametersyay, dataCopy)
        except Exception as e:
            if arguments["silent"] is False:
                print(Fore.RED + "FAIL" + Fore.RESET+ ", Reason: {}".format(e))
            else:
                print(e)
                print(Fore.RED+"{} failed with error {}".format(filename, e))
            exit()
        if arguments["silent"] is False:
            print(Fore.GREEN+"OK"+Fore.RESET)

        if config["backupIntentFiles"]==True:
            shutil.copy2(mainPath + filename, mainPath + "bkup/")
        if config["createDoneFolder"]==True:
            os.rename(mainPath + filename, mainPath + "done/" + re.sub(".json","",filename) + "-ADDED-" + re.sub("\/","-",re.sub(":",".",re.sub(" ", "_", time.strftime("%x_%X")))) + ".json")
            
def delete_intents():
    if arguments["silent"] is False:
        print("Checking if access to DialogFlow is granted...")
    try:
        list_intents(config['project_id'])
    except Exception as e :
        print("Access Denied, Reason: {}".format(e))
        exit()
    if arguments["silent"] is False:        
        print(Fore.GREEN + "Access Granted!" + Fore.RESET)

    if not os.path.isfile(mainPath):

        filenames = next(os.walk(mainPath), (None, None, []))[2]
        # remove .gitkeep
        try:
            filenames.remove(".gitkeep")
        except:
            pass
        if len(filenames) == 0:
            print(Fore.RED + "No intents found in {}, exiting...".format(mainPath) + Fore.RESET)
            exit()
        newfiles = []
        if arguments["silent"] is False:
            print("Doing checks against the files...\n")
        for filename in filenames:
            if arguments["silent"] is False:
                print("Checking {}... ".format(filename), end="")
            if filename.endswith(".json"):
                try:
                    data = json.load(open(mainPath + filename))
                except:
                    print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "invalid data"))
                    exit()
                if "name" not in data:
                    print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "intent has no name"))
                    exit()
                if "userSays" not in data:
                    print(Fore.RED +"FAIL"+Fore.RESET+", Reason: {}".format( "intent has no userSys"))
                    exit()
                if len(data["userSays"]) == 0:
                    print(Fore.RED + "FAIL"+Fore.RESET+", Reason: {}".format( "intent has no items in userSys"))
                    exit()
                if arguments["silent"] is False:
                    print(Fore.GREEN+"OK"+Fore.RESET)

                newfiles.append(filename)
            else:
                print("FAIL"+Fore.RESET+", {}".format( "not .json"))
            
        for filename in newfiles:
            data = json.load(open(mainPath + filename))
            if arguments["silent"] is False:
                print("Deleting intent with name '{}' specified by '{}'... ".format(data["name"], filename), end="")
            intentName = data["name"]
            if get_intent(config['project_id'], intentName) is None:
                if arguments["silent"] is False:
                    print(Fore.LIGHTBLACK_EX+"SKIPPED, doesntexist"+Fore.RESET)
                continue
            try:
                intentId = get_intent(config['project_id'], intentName).name
                intentId= re.sub(r'.*/', '', intentId)
                delete_intent(config['project_id'], intentId)
            except Exception as e:
                if arguments["silent"] is False:
                    print(Fore.RED + "FAIL"+ Fore.RESET+", Reason: {}".format(e))
                else:
                    print(Fore.RED+"{} failed with error {}".format(filename, e))
                exit()
            if arguments["silent"] is False:
                print(Fore.GREEN+"OK"+Fore.RESET)
            if config["backupIntentFiles"]==True:
                shutil.copy2(mainPath + filename, mainPath + "bkup/")
            if config["createDoneFolder"]==True:
                os.rename(mainPath + filename, mainPath + "done/" + re.sub(".json","",filename) + "-DELETED-" + re.sub("\/","-",re.sub(":",".",re.sub(" ", "_", time.strftime("%x_%X")))) + ".json")
    else:
        intentsToRemove = []
        with open(mainPath, "r") as f:
            intentsToRemove = f.read().splitlines()
        for intent in intentsToRemove:
            if intent == "fallback":
                intent = get_fallback_intent(config['project_id']).display_name
            if arguments["silent"] is False:
                print("Deleting intent with name '{}'... ".format(intent), end="")
            if get_intent(config['project_id'], intent) is None:
                if arguments["silent"] is False:
                    print(Fore.LIGHTBLACK_EX+"SKIPPED, doesntexist"+Fore.RESET)
                continue
            try:
                intentId = get_intent(config['project_id'], intent).name
                intentId= re.sub(r'.*/', '', intentId)
                delete_intent(config['project_id'], intentId)
            except Exception as e:
                if arguments["silent"] is False:
                    print(Fore.RED + "FAIL"+ Fore.RESET+", Reason: {}".format(e))
                else:
                    print(Fore.RED+"{} failed with error {}".format(intent, e))
                exit()
            if arguments["silent"] is False:
                print(Fore.GREEN+"OK"+Fore.RESET)


def banner():
    print(Fore.YELLOW + """
[==========================================================]"""+Fore.RESET+"""
                 DialogFlow Intent Manager
    
     Created by:
         @InimicalPart ("""+Fore.CYAN+"""https://github.com/InimicalPart"""+Fore.RESET+""")
""" + Fore.YELLOW + """[==========================================================]
    """ + Fore.RESET)

def main():
    if arguments["silent"] is False and arguments["no_banner"] is False:
        banner()
    if arguments["create"] is False and arguments["delete"] is False and arguments["list"] is False:
        print("""
    Choose an option:
        1. Create intents
        2. Delete intents
            """)
        option = input("Option: ")
        if option == "1":
            print("\n\nAdd all intents that you want to create to the " + mainPath + " folder and press enter when done")
            input()
            create_intents()
        elif option == "2":
            print("\n\nAdd all intents that you want to delete to the " + mainPath + " folder and press enter when done")
            input()
            delete_intents()
        elif option == "3":
            print(get_fallback_intent(config['project_id']))
    else:
        if arguments["create"] is True:
            create_intents()
        elif arguments["delete"] is True:
            delete_intents()
        elif arguments["list"] is True:
            print(list_intents("", arguments["only_names"] is True))



if __name__ == "__main__":
    main()
