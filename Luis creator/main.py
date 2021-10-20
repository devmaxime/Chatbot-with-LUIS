from sources.initialize_luis import InitializeLuis
from sources.prepare_data import Prepare

import json, time

with open("auth/authoring.json") as f: #Retrieving the key and endpoint from a hidden file
    authoring_keys = json.load(f)

authoringKey = authoring_keys.get('authoringKey')
authoringEndpoint = authoring_keys.get('authoringEndpoint')
sampleSize = 1000
batchSize = 20

def chunk_list (list, x):
    return [list[i:i+x] for i in range(0, len(list), x)]

if __name__ == '__main__':
    LuisApp = InitializeLuis(authoringKey, authoringEndpoint)
    Data = Prepare(sampleSize)
    print('Initialization and data preparation complete. Let\'s execute the content of main.py.')

    print('Generating batchs..', end="")
    labelsToSend = []
    for i in range(0, sampleSize):        
        labeledUtterance = Data.createLabel(LuisApp.intentName, Data.prepared_sample.iloc[i])
        labelsToSend.append(labeledUtterance)
    print('done')

    print('Uploading batch..', end="")
    chunks = chunk_list(labelsToSend, batchSize)

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
    #LuisApp.client.azure_accounts.assign_to_app()
    LuisApp.client.apps.update_settings(LuisApp.app_id, is_public=True)
    responseEndpointInfo = LuisApp.client.apps.publish(LuisApp.app_id, LuisApp.versionId, is_staging=False)
    print('done')

    print(responseEndpointInfo) 
    #TODO: Add ressources to the app and publish it really.

    # runtimeCredentials = CognitiveServicesCredentials(predictionKey)
    # clientRuntime = LUISRuntimeClient(endpoint=predictionEndpoint, credentials=runtimeCredentials) 