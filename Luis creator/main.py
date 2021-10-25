from sources.initialize_luis import InitializeLuis
from sources.prepare_data import Prepare
from sources.evaluate_luis import Evaluate

import json, time
from pandas import read_json

with open("config.json") as f: #Retrieving config from config.json
    CONFIG = json.load(f)

with open(CONFIG.get('authPath')) as f: #Retrieving the key and endpoint from a hidden file
    AUTHORING = json.load(f)    
authoringKey = AUTHORING.get('authoringKey')
authoringEndpoint = AUTHORING.get('authoringEndpoint')

def chunk_list (list, x):
    return [list[i:i+x] for i in range(0, len(list), x)]

if __name__ == '__main__':
    LuisApp = InitializeLuis(authoringKey, authoringEndpoint, CONFIG) #Initialize Luis application

    frames = read_json(CONFIG.get('framesPath')) #Load frames to sent before sending it to preparation
    Data = Prepare(CONFIG.get('trainSize'), frames)    
    print('Initialization and data preparation complete. Let\'s execute the content of the code in main.py.')

    print('Generating batchs..', end="")
    labelsToSend = []
    for i in range(0, CONFIG.get('trainSize')):        
        labeledUtterance = Data.createLabel(LuisApp.intentName, Data.prepared_sample.iloc[i])
        labelsToSend.append(labeledUtterance)
    print('done')

    print('Uploading batch..', end="")
    chunks = chunk_list(labelsToSend, CONFIG.get('batchSize'))

    for chunk in chunks:
        try:
            LuisApp.client.examples.batch(LuisApp.app_id, LuisApp.versionId, chunk)
        except Exception as err:
            print("Encountered exception. {}".format(err))
    print('done')

    print('Training..', end="")
    LuisApp.client.train.train_version(LuisApp.app_id, LuisApp.versionId)
    waiting = True
    while waiting:
        info = LuisApp.client.train.get_status(LuisApp.app_id, LuisApp.versionId)
        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            time.sleep(10)
        else: 
            print ("done")
            waiting = False

    print('Publishing..', end="")
    LuisApp.client.apps.update_settings(LuisApp.app_id, is_public=True)
    responseEndpointInfo = LuisApp.client.apps.publish(LuisApp.app_id, LuisApp.versionId, is_staging=False)
    print('done')

    print(responseEndpointInfo) 

    Evaluation = Evaluate(CONFIG.get('testSize'), frames, CONFIG.get('trainSize'), authoringKey, authoringEndpoint, LuisApp.app_id)