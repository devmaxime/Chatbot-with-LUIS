from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from msrest.authentication import CognitiveServicesCredentials

import uuid

class InitializeLuis():
    def __init__(self, authoringKey : str, authoringEndpoint : str, CONFIG):
        self.authoringKey = authoringKey
        self.authoringEndpoint = authoringEndpoint
        self.CONFIG = CONFIG

        self.initializeApp()
        self.initializeEntities()
        self.initializeIntents()

    def get_child_id(self, model, childName):	
        """
        Return the children id of an element.
        """
        theseChildren = next(filter((lambda child: child.name == childName), model.children))        
        return theseChildren.id

    def initializeApp(self):
        """
        Create a luis app according to the CONFIG.
        """
        appName = self.CONFIG.get('appName') + " " + str(uuid.uuid4())
        self.versionId = self.CONFIG.get('versionId')
        self.intentName = self.CONFIG.get('intentName')
        self.entityName = self.CONFIG.get('entityName')

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
        """
        Create all the machine learned entities for the project. Add the prebuilt features to the entities.
        """
        mlEntityDefinition = [
            { "name": "or_city" },
            { "name": "dst_city" },
            { "name": "budget" },
            { "name": "str_date" },
            { "name": "end_date" }
        ]

        try:
            modelId = self.client.model.add_entity(self.app_id, self.versionId, name=self.entityName, children=mlEntityDefinition) #Adding the entity definition

            self.client.model.add_prebuilt(self.app_id, self.versionId, prebuilt_extractor_names=["number"]) #Adding prebuilt features   
            self.client.model.add_prebuilt(self.app_id, self.versionId, prebuilt_extractor_names=["datetimeV2"])
            self.client.model.add_prebuilt(self.app_id, self.versionId, prebuilt_extractor_names=["geographyV2"])            

            modelObject = self.client.model.get_entity(self.app_id, self.versionId, modelId) #Linking prebuilt features to entity

            budgetId = self.get_child_id(modelObject, "budget") #Adding number prebuilt to budget
            prebuiltFeatureRequiredDefinition = { "model_name": "number" } 
            self.client.features.add_entity_feature(self.app_id, self.versionId, budgetId, prebuiltFeatureRequiredDefinition)

            str_dateId = self.get_child_id(modelObject, "str_date") #Adding number prebuilt to str_date
            prebuiltFeatureRequiredDefinition = { "model_name": "datetimeV2" } 
            self.client.features.add_entity_feature(self.app_id, self.versionId, str_dateId, prebuiltFeatureRequiredDefinition)

            end_dateId = self.get_child_id(modelObject, "end_date") #Adding number prebuilt to end_date
            prebuiltFeatureRequiredDefinition = { "model_name": "datetimeV2" } 
            self.client.features.add_entity_feature(self.app_id, self.versionId, end_dateId, prebuiltFeatureRequiredDefinition)

            or_cityId = self.get_child_id(modelObject, "or_city") #Adding number prebuilt to or_city
            prebuiltFeatureRequiredDefinition = { "model_name": "geographyV2" } 
            self.client.features.add_entity_feature(self.app_id, self.versionId, or_cityId, prebuiltFeatureRequiredDefinition)

            dst_cityId = self.get_child_id(modelObject, "dst_city") #Adding number prebuilt to dst_city
            prebuiltFeatureRequiredDefinition = { "model_name": "geographyV2" } 
            self.client.features.add_entity_feature(self.app_id, self.versionId, dst_cityId, prebuiltFeatureRequiredDefinition)

            print("Created ML Entity.")
        except Exception as err:
            print("Encountered exception. {}".format(err))
            self.error = err    
            print("You may need to verify the definition of your entity, the name of the entity, the prebuilt features or the app parameters.")

    def initializeIntents(self):
        """
        Create the needed intent.
        """
        try:
            self.client.model.add_intent(self.app_id, self.versionId, self.intentName)
            print('Created Intent.')
        except Exception as err:
                print("Encountered exception. {}".format(err))
                self.error = err    