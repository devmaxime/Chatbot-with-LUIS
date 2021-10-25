from sources.prepare_data import Prepare

from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

import numpy as np

class Score:
    def __init__(self):
        self._intents = []
        self.ratioIntents = 0


class Evaluate:
    def __init__(self, testSize, raw, trainSize, authoringKey, authoringEndpoint, LuisAppId) -> None:
        self._client = LUISRuntimeClient(authoringEndpoint,   CognitiveServicesCredentials(authoringKey))
        self.score = Score()
        self._testData = Prepare(trainSize, raw, testSize)
        self._appId = LuisAppId

        self.evaluating(self._testData)
        print(self.score.ratioIntents)

        exit()

    def countIntent(self, row) -> int:
        """
        countIntent counts how many columns there is in a row while excluding the column named "text".
        """
        _score = 0
        _row = row.drop('text')
        for _, item in _row.items():
            if (item != 'none' and item != 0):
                _score = _score + 1
        return _score


    def evaluating(self, testData) -> None:
        """
        Execute all the evaluations.
        """
        for _, row in testData.prepared_sample.iterrows():
            intentNumber = self.countIntent(row)
            if(intentNumber > 0): #Avoid division by zero
                self.evaluateIntentnumber(row, self.countIntent(row))            
        self.score.ratioIntents = np.round(np.mean(self.score._intents), 3)
        


    def evaluateIntentnumber(self, query, intentNumber) -> None:
        """
        evaluateIntentNumber compares how many intents the LuisApp found versus how many intents it's supposed to find.
        """
        _text = query['text']

        try:
            result = self._client.prediction.get_slot_prediction(
                self._appId,
                "Production",
                prediction_request = { "query" : _text }                
            )
        except Exception as err:
            print("Encountered exception. {}".format(err))
            
        if(bool(result.prediction.entities)): #Check if not empty
            self.score._intents.append(len(result.prediction.entities['ticketBooking'][0]) / intentNumber)