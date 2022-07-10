from google.api_core.exceptions import InvalidArgument
import google.cloud.dialogflow_v2 as dialogflow
import os
import json

from requests import session
config = json.load(open('config.json'))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['authFile']
session_client = dialogflow.SessionsClient()
session = session_client.session_path(config['project_id'], "created_by_inimicalpart")
