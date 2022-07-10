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
    for intent in intents:
        print("=" * 20)
        print("Intent name: {}".format(intent.name))
        print("Intent display_name: {}".format(intent.display_name))
        print("Action: {}\n".format(intent.action))
        print("Root followup intent: {}".format(intent.root_followup_intent_name))
        print("Parent followup intent: {}\n".format(intent.parent_followup_intent_name))
        print("Input contexts:")
        for input_context_name in intent.input_context_names:
            print("\tName: {}".format(input_context_name))
        print("Output contexts:")
        for output_context in intent.output_contexts:
            print("\tName: {}".format(output_context.name))
        print(intent)

def create_intent(project_id, display_name, training_phrases_parts, message_texts, entities):
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
list_intents(config['project_id'])
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
            trainingPhrases.append(userSays["data"])
        for response in data["responses"]:
            responses.append(response["data"].text)
        
