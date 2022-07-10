from google.api_core.exceptions import InvalidArgument
import google.cloud.dialogflow_v2 as dialogflow
import os
import json
config = json.load(open('config.json'))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['authFile']
