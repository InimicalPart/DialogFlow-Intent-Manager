from google.api_core.exceptions import InvalidArgument
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
    intents = intents_client.list_intents(request={"parent": parent})
    return intents
        

def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        # Here we create a new training phrase for each provided part.
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)
    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
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
    print(intent.display_name)
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
            #if userSays["data"] is a list 
            if isinstance(userSays["data"], list):
                for data in userSays["data"]:
                    trainingPhrases.append(data)
            else:
                trainingPhrases.append(userSays["data"])
            # trainingPhrases.append(userSays["data"])
        if "response" in userSays:
            for response in data["responses"]:
                responses.append(response["data"])
        
        print("{}\n\n{}\n\n{}".format(intentName, trainingPhrases, responses))

        # intenter = dialogflow.Intent()
        # intenter.display_name = intentName
        # intenter.training_phrases = trainingPhrases
        # intenter.messages = [dialogflow.Intent.Message(text=dialogflow.Intent.Message.Text(text=responses))]
        # print(intenter)




        create_intent(config['project_id'], intentName, trainingPhrases, responses)
        
