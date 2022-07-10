import google.cloud.dialogflow_v2 as dialogflow
import os
import json

try:
    config = json.load(open('config.json'))
except:
    print('config.json not found or invalid')
    exit()

try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['authFile']
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(config['project_id'], "created_by_inimicalpart")
except:
    print('authFile not found/invalid, or project_id not found')
    exit()

def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    intents = intents_client.list_intents(request={"parent": parent, "IntentView": "INTENT_VIEW_FULL"})
    return intents
        

def create_intent(project_id, display_name, training_phrases_parts, message_texts, parameters):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_prt in training_phrases_parts:
        print("Looping through training phrases parts, current part: {}".format(training_phrases_prt))
        parts = []
        for training_phrases_part in training_phrases_prt:
            print("Looping through training phrase parts, current part: {}".format(training_phrases_part))
            if isinstance(training_phrases_part, dict):
                print("Training phrase part is a dict")
                if "userDefined" in training_phrases_part:
                    if training_phrases_part["userDefined"] == True:
                        print("Training phrase part is a user defined part (parameter)")
                        parts.append(dialogflow.types.Intent.TrainingPhrase.Part(
                            text=training_phrases_part['text'],
                            entity_type=training_phrases_part['entityType'],
                            alias=training_phrases_part['alias'],
                            
                            
                        ))
                        print(parts[-1])
                    else:
                      print("Training phrase part is not a user defined part (normal text)")
                      parts.append(dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part["text"]))

            else:
                print("Training phrase part is not a dict (text)")
                parts.append(dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part))
        print("\n\nTraining phrase parts: {}\n\n".format(parts))
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=parts)
        training_phrases.append(training_phrase)

        # Here we create a new training phrase for each provided part.
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    if parameters:
        print("Parameters: {}".format(parameters))
        for parameter in parameters:
            print("Parameter: {}".format(parameter))
            parameter_type = dialogflow.Intent.Parameter.Type(choice=parameter['type'])
            print("Parameter type: {}".format(parameter_type))
            parameter = dialogflow.Intent.Parameter(
                display_name=parameter['displayName'],
                value_spec=dialogflow.Intent.Parameter.ValueSpec(
                    list_value_spec=dialogflow.Intent.Parameter.ListValueSpec(
                        items=[dialogflow.Intent.Parameter.ListValueSpec.Item(
                            value=parameter['value'])]
                    ),
                    type=parameter_type
                )
            )
            print("Parameter: {}".format(parameter))
            message.add_parameter(parameter)
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]

    )
    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )
    print("Intent created: {}".format(response))

print("Listing Intents...")
# testing = list_intents(config['project_id'])
# with open('intents.json', 'w') as outfile:
#     outfile.write(str(testing))
# print("Intents listed!")
for intent in list_intents(config['project_id']):
    print("\n\n{}\n\n".format(intent))
    # print("\n")
filenames = next(os.walk("./intents/"), (None, None, []))[2]  # [] if no file
if len(filenames) == 0:
    print("No intents found, exiting...")
    exit()

print("Doing checks against the files...")
for filename in filenames:
    print("Checking {}...".format(filename))
    if filename.endswith(".json"):
        print("{} is a json file, checking...".format(filename))
        try:
            data = json.load(open("./intents/" + filename))
        except:
            print("{} is invalid, Reason: {}".format(filename, "doesn't contain proper json data"))
            exit()
        print("{} contains valid JSON data, checking...".format(filename))
        if "name" not in data:
            print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain a name"))
            exit()
        if "userSays" not in data:
            print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain userSays"))
            exit()
        if len(data["userSays"]) == 0:
            print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain any userSays"))
            exit()
        
        print("{} is valid, creating intent...".format(filename))
        trainingPhrases = []
        responses = []
        intentName = data["name"]
        for userSays in data["userSays"]:
            a = []
            print("\n\nUSERSYS: {}".format(userSays))
            #if userSays["data"] is a list 
            if isinstance(userSays["data"], list):
                for data in userSays["data"]:
                    if "userDefined" in data:
                        if data["userDefined"] == False:
                            a.append(data["text"])
                            # trainingPhrases.append(data["text"])
                        else:
                            newObj = {}
                            newObj["text"] = data["text"]
                            newObj["userDefined"] = True
                            newObj["entityType"] = data["meta"]
                            newObj["alias"] = data["alias"]
                            a.append(newObj)
                            # trainingPhrases.append(newObj)
            else:
                trainingPhrases.append(userSays["data"].text)
            
            trainingPhrases.append(a)
        print("\n\nTRAINING PHRASES: {}".format(trainingPhrases))
        if "responses" in data:
            for response in data["responses"]:
                if "messages" in response:
                    if len(response["messages"]) > 0:
                        if "speech" in response["messages"][0]:
                            responses = response["messages"][0]["speech"]
                        else:
                            print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain any text"))
                            exit()
                    else:
                        print("{} is invalid, Reason: {}".format(filename, "intent doesn't contain any messages"))
                        exit()
        

        print("{}\n\n{}\n\n{}".format(intentName, trainingPhrases, responses))

        # intenter = dialogflow.Intent()
        # intenter.display_name = intentName
        # intenter.training_phrases = trainingPhrases
        # intenter.messages = [dialogflow.Intent.Message(text=dialogflow.Intent.Message.Text(text=responses))]
        # print(intenter)




        create_intent(config['project_id'], intentName, trainingPhrases, responses)
        
