from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from msrest.authentication import CognitiveServicesCredentials

import uuid

class InitializeLuis():
    def __init__(self, authoringKey : str, authoringEndpoint : str):
        self.authoringKey = authoringKey
        self.authoringEndpoint = authoringEndpoint

        self.initializeApp()
        self.initializeEntities()
        self.initializeIntents()

    def initializeApp(self):
        appName = "Booking Flight " + str(uuid.uuid4())
        self.versionId = "0.1"
        self.intentName = "bookingIntent"

        self.client = LUISAuthoringClient(self.authoringEndpoint, CognitiveServicesCredentials(self.authoringKey))
    
        try:
            appDefinition = ApplicationCreateObject (name=appName, initial_version_id=self.versionId, culture='en-us')
            self.app_id = self.client.apps.add(appDefinition)
            print("Created LUIS app with ID {}".format(self.app_id))

        except Exception as err:

            print("Encountered exception. {}".format(err))
            self.error = err    
            print("You may need to verify the name of your app, the key or the endpoint.")

    def initializeEntities(self):
        mlEntityDefinition = mlEntityDefinition = [
            { "name": "or_city" },
            { "name": "dst_city" },
            { "name": "budget" },
            { "name": "str_date" },
            { "name": "end_date" }
        ]

        try:            
            self.client.model.add_entity(self.app_id, self.versionId, name="ticketBooking", children=mlEntityDefinition)
            print("Created ML Entity.")
        except Exception as err:
            print("Encountered exception. {}".format(err))
            self.error = err    
            print("You may need to verify the definition of your entity, the name of the entity and the app parameters.")

    def initializeIntents(self):
        try:
            self.client.model.add_intent(self.app_id, self.versionId, self.intentName)
            print('Created Intent.')
        except Exception as err:
                print("Encountered exception. {}".format(err))
                self.error = err    