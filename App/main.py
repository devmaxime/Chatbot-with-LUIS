from sources.initialize_luis import InitializeLuis
from sources.prepare_data import Prepare

authoringKey = 'ef26b6777f96406cbdcea4e7e6d50dcc'
authoringEndpoint = 'https://westeurope.api.cognitive.microsoft.com/'
sampleSize = 10

if __name__ == '__main__':
    BookFlight = InitializeLuis(authoringKey, authoringEndpoint)
    Data = Prepare(sampleSize)

    print('Adding utterances..')
    for i in range(0, sampleSize):
        
        labeledUtterance = Data.createLabel(BookFlight.intentName, Data.prepared_sample.iloc[i])
        print(labeledUtterance)
        try:
            BookFlight.client.examples.add(BookFlight.app_id, BookFlight.versionId, labeledUtterance)
        except Exception as err:
            print("Encountered exception. {}".format(err))  