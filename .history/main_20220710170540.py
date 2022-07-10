import re
import time
import google.cloud.dialogflow_v2 as dialogflow
import os
import json

try:
    config = json.load(open('config.json'))
except:
    print('config.json not found or is invalid')
    exit()

try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['authFile']
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(config['project_id'], "created_by_inimicalpart")
except:
    print('{} not found, is invalid, or project not found on DialogFlow'.format(config['authFile']))
    exit()

def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent})
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

def create_intent(project_id, display_name, training_phrases_parts, message_texts, parameters=[]):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_prt in training_phrases_parts:
        parts = []
        for training_phrases_part in training_phrases_prt:
            if isinstance(training_phrases_part, dict):
                if "userDefined" in training_phrases_part:
                    if training_phrases_part["userDefined"] == True:
                        parts.append(dialogflow.types.Intent.TrainingPhrase.Part(
                            text=training_phrases_part['text'],
                            entity_type=training_phrases_part['entityType'],
                            alias=training_phrases_part['alias'],
                            
                            
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
    response = intents_client.create_intent(
        request={"parent": parent, "intent": dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
        parameters=newParameters
    )}
    )
    print("Intent created: {}".format(response.display_name))

def create_intent_from_files():
    print("Checking if I can list Intents...")
    try:
        list_intents(config['project_id'])
    except Exception as e :
        print("Intents list failed! {}".format(e))
        exit()
    print("Intents list successful!")

    filenames = next(os.walk("./intents/"), (None, None, []))[2]
    newfiles = []
    if len(filenames) == 0:
        print("No intents found in ./intents/, exiting...")
        exit()

    print("Doing checks against the files...")
    for filename in filenames:
        print("Checking {}...".format(filename), end="")
        if filename.endswith(".json"):
            try:
                data = json.load(open("./intents/" + filename))
            except:
                print("{} is invalid, Reason: {}".format(filename, "doesn't contain proper json data"))
                exit()
            if "name" not in data:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain a name"))
                exit()
            if "userSays" not in data:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain userSays"))
                exit()
            if len(data["userSays"]) == 0:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain any userSays"))
                exit()
            print("OK")
            newfiles.append(filename)
        else:
            print("{} is invalid, Reason: {}".format(filename, "doesn't have .json extension"))
        
    for filename in newfiles:
            
        trainingPhrases = []
        responses = []
        dataCopy = data.copy()
        intentName = data["name"]
        if get_intent(config['project_id'], intentName) is not None:
            print("{} already exists, skipping...".format(intentName))
            continue
        for userSays in data["userSays"]:
            a = []
            if isinstance(userSays["data"], list):
                for data in userSays["data"]:
                    if "userDefined" in data:
                        if data["userDefined"] == False:
                            a.append(data["text"])
                        else:
                            newObj = {}
                            newObj["text"] = data["text"]
                            newObj["userDefined"] = True
                            newObj["entityType"] = data["meta"]
                            newObj["alias"] = data["alias"]
                            a.append(newObj)
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
            create_intent(config['project_id'], intentName, trainingPhrases, responses, parametersyay)
        except Exception as e:
            print("{} failed to create intent, Reason: {}".format(intentName, e))
            exit()
        os.rename("./intents/" + filename, "./intents/done/" + re.sub(".json","",filename) + "-ADDED-" + re.sub("\/","-",re.sub(":",".",re.sub(" ", "_", time.strftime("%x_%X")))) + ".json")
            
def delete_intents():
    print("Checking if I can list Intents...")
    try:
        list_intents(config['project_id'])
    except Exception as e :
        print("Intents list failed! {}".format(e))
        exit()
    print("Intents list successful!")

    filenames = next(os.walk("./intents/"), (None, None, []))[2]
    if len(filenames) == 0:
        print("No intents found in ./intents/, exiting...")
        exit()
    newfiles = []
    print("Doing checks against the files...")
    for filename in filenames:
        print("Checking {}...".format(filename), end="")
        if filename.endswith(".json"):
            try:
                data = json.load(open("./intents/" + filename))
            except:
                print("{} is invalid, Reason: {}".format(filename, "doesn't contain proper json data"))
                exit()
            if "name" not in data:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain a name"))
                exit()
            if "userSays" not in data:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain userSays"))
                exit()
            if len(data["userSays"]) == 0:
                print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain any userSays"))
                exit()
            print("OK")
            newfiles.append(filename)
        else:
            print("{} is invalid, Reason: {}".format(filename, "doesn't have .json extension"))
        
    for filename in newfiles:
        intentName = data["name"]
        print("Deleting intent with name '{}' specified by '{}'...".format(data["name"], filename), end="")
        if get_intent(config['project_id'], intentName) is None:
            print("SKIPPED, doesntexist")
            continue
        try:
            intentId = get_intent(config['project_id'], intentName).name
            intentId= re.sub(r'.*/', '', intentId)
            delete_intent(config['project_id'], intentId)
        except Exception as e:
            print("FAIL, {}".format(intentName, e))
            exit()
        print("OK")
        os.rename("./intents/" + filename, "./intents/done/" + re.sub(".json","",filename) + "-DELETED-" + re.sub("\/","-",re.sub(":",".",re.sub(" ", "_", time.strftime("%x_%X")))) + ".json")
def banner():
    print("""
==========================================================
                DialogFlow Intent Manager
    
    Created by:
        @InimicalPart (https://github.com/InimicalPart)
==========================================================
    """)

def main():
    banner()
    print("""
Choose an option:
    1. Create intents
    2. Delete intents
        """)
    option = input("Option: ")
    if option == "1":
        print("Add all intents that you want to add to the ./intents/ folder and press enter when done")
        input()
        create_intent_from_files()
    elif option == "2":
        print("Add all intents that you want to delete to the ./intents/ folder and press enter when done")
        input()
        delete_intents()



if __name__ == "__main__":
    # print(get_intent(config['project_id'], "waweofnwoeifnion").name)
    main()