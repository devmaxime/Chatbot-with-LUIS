from sources.initialize_luis import InitializeLuis
from sources.prepare_data import Prepare

import json

with open("auth/authoring.json") as f: #Retrieving the key and endpoint from a hidden file
    authoring_keys = json.load(f)

authoringKey = authoring_keys.get('authoringKey')
authoringEndpoint = authoring_keys.get('authoringEndpoint')
sampleSize = 20
batchSize = 20

def chunk_list (list, x):
    return [list[i:i+x] for i in range(0, len(list), x)]

if __name__ == '__main__':
    BookFlight = InitializeLuis(authoringKey, authoringEndpoint)
    Data = Prepare(sampleSize)

    print('Generating batchs..')
    labelsToSend = []
    for i in range(0, sampleSize):        
        labeledUtterance = Data.createLabel(BookFlight.intentName, Data.prepared_sample.iloc[i])
        labelsToSend.append(labeledUtterance)

    print('Uploading batch..')
    chunks = chunk_list(labelsToSend, batchSize)

    for chunk in chunks:
        try:
            BookFlight.client.examples.batch(BookFlight.app_id, BookFlight.versionId, chunk)
        except Exception as err:
            print("Encountered exception. {}".format(err))

  