from sources.prepare_data import Prepare

from difflib import SequenceMatcher

from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

import numpy as np

def check_key_exist(test_dict, key):
    try:
       value = test_dict[key]
       return True
    except KeyError:
        return False

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class Score:
    def __init__(self):
        self._intentsNumber = []
        self.ratioIntentsNumber = 0

        self._intentsRightness = []
        self.ratioIntentsRightness = 0

        self._intentsAlmostRightness = []
        self.ratioIntentsAlmostRightness = 0

        self.accuracy = dict(
            str_date = [],
            end_date = [],
            budget = [],
            or_city = [],
            dst_city = []
        )

        self.Almostaccuracy = dict(
            str_date = [],
            end_date = [],
            budget = [],
            or_city = [],
            dst_city = []
        )


class Evaluate:
    def __init__(self, testSize, raw, trainSize, authoringKey, authoringEndpoint, LuisAppId) -> None:
        print('==== EVALUATION START ====')
        self._client = LUISRuntimeClient(authoringEndpoint,   CognitiveServicesCredentials(authoringKey))
        self.score = Score()
        self._testData = Prepare(trainSize, raw, testSize)
        self._appId = LuisAppId

        self.evaluating(self._testData)
        print('Entities number score', self.score.ratioIntentsNumber)
        print('Exact entity score', self.score.ratioIntentsRightness)
        print('Exact entity score by entities', self.score.accuracy)

        print('Almost exact entity score', self.score.ratioIntentsAlmostRightness)
        print('Almost exact entity score by entities', self.score.Almostaccuracy)
        print('==== EVALUATION END ====')

        

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
        Query Luis with some text then execute all the evaluations.
        """
        for _, row in testData.prepared_sample.iterrows():
            _text = row['text']
            try:
                result = self._client.prediction.get_slot_prediction(
                    self._appId,
                    "Production",
                    prediction_request = { "query" : _text }                
                )
            except Exception as err:
                print("Encountered exception. {}".format(err))

            # Tests
            self.evaluateIntentNumber(row, result)   
            self.evaluateIntentRightness(row, result)

        # Calculate means             
        self.score.ratioIntentsNumber = np.round(np.mean(self.score._intentsNumber), 3)  
        self.score.ratioIntentsRightness = np.round(np.mean(self.score._intentsRightness), 3)
        self.score.ratioIntentsAlmostRightness = np.round(np.mean(self.score._intentsAlmostRightness), 3)

        for acc in self.score.accuracy:
            self.score.accuracy[acc] = np.round(np.mean(self.score.accuracy[acc]), 3)  

        for acc in self.score.Almostaccuracy:
            self.score.Almostaccuracy[acc] = np.round(np.mean(self.score.Almostaccuracy[acc]), 3)      


    def evaluateIntentNumber(self, row, queryResult) -> None:
        """
        evaluateIntentNumber compares how many intents the LuisApp found versus how many intents it's supposed to find.
        """
        intentNumber = self.countIntent(row)
        if(intentNumber > 0 and check_key_exist(queryResult.prediction.entities, 'ticketBooking')): #Avoid division by zero and empty query result.
            self.score._intentsNumber.append(len(queryResult.prediction.entities['ticketBooking'][0]) / intentNumber)

    def evaluateIntentRightness(self, row, queryResult) -> None:
        """
        evaluateIntentRightness compares the returned intent versus the original intent.
        """
        _score1 = []
        _score2 = []
        if(check_key_exist(queryResult.prediction.entities, 'ticketBooking')): #Avoid empty query result.
            for item in queryResult.prediction.entities['ticketBooking'][0].items():
                if(row[item[0]] == item[1][0]): #Exact match
                    self.score.accuracy[item[0]].append(1)
                    _score1.append(1)
                else:
                    self.score.accuracy[item[0]].append(0)
                    _score1.append(0)
                if(similar(str(row[item[0]]), str(item[1][0])) > 0.90): #Almost match
                    self.score.Almostaccuracy[item[0]].append(1)
                    _score2.append(1)
                else:
                    self.score.Almostaccuracy[item[0]].append(0)
                    _score2.append(0)

        if(bool(_score1)):
            self.score._intentsRightness.append(np.round(np.mean(_score1), 3))
        else:
            self.score._intentsRightness.append(0)
        if(bool(_score2)):
            self.score._intentsAlmostRightness.append(np.round(np.mean(_score2), 3))
        else:
            self.score._intentsAlmostRightness.append(0)    
       